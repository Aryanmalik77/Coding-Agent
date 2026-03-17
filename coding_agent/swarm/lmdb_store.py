"""LMDB-backed state store for the coding agent."""

import json
import os
from pathlib import Path
from typing import Any, Iterator, Optional

import lmdb
import msgpack
from loguru import logger


class LMDBStore:
    """
    Zero-latency key-value store based on LMDB.
    """

    def __init__(self, workspace: Path, db_name: str = "coding_agent_state.lmdb", map_size: Optional[int] = None):
        self.db_path = Path(workspace) / db_name
        
        # Default to 500MB if not specified, or use environment variable
        if map_size is None:
            map_size = int(os.getenv("LMDB_MAP_SIZE", 500 * 1024 * 1024))
        
        # Ensure parent directories exist
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize LMDB environment
        self.env = lmdb.open(
            str(self.db_path),
            map_size=map_size,
            max_dbs=1,
            lock=True,
            sync=True,
        )
        self.db = self.env.open_db(b"primary")
        logger.debug("Initialized LMDB store at {}", self.db_path)

    def _serialize(self, value: Any) -> bytes:
        try:
            return msgpack.packb(value, use_bin_type=True)
        except (TypeError, ValueError):
             return json.dumps(value).encode("utf-8")

    def _deserialize(self, value: bytes) -> Any:
        try:
            return msgpack.unpackb(value, raw=False)
        except (msgpack.exceptions.ExtraData, msgpack.exceptions.FormatError, TypeError, ValueError):
            return json.loads(value.decode("utf-8"))

    def get(self, key: str, default: Any = None) -> Any:
        with self.env.begin(db=self.db) as txn:
            data = txn.get(key.encode("utf-8"))
            if data is None:
                return default
            try:
                return self._deserialize(data)
            except Exception as e:
                logger.error("Failed to deserialize value for {}: {}", key, e)
                return default

    def put(self, key: str, value: Any) -> None:
        try:
            serialized_val = self._serialize(value)
            with self.env.begin(write=True, db=self.db) as txn:
                txn.put(key.encode("utf-8"), serialized_val)
        except Exception as e:
            logger.error("Failed to store value for {}: {}", key, e)

    def delete(self, key: str) -> bool:
        with self.env.begin(write=True, db=self.db) as txn:
            return txn.delete(key.encode("utf-8"))

    def list_keys(self, limit: int = 1000) -> list[str]:
        """Fetch a limited list of keys to avoid memory issues."""
        keys = []
        with self.env.begin(db=self.db) as txn:
            cursor = txn.cursor()
            for i, (k, _) in enumerate(cursor):
                if i >= limit:
                    break
                keys.append(k.decode("utf-8"))
        return keys

    def iter_keys(self) -> Iterator[str]:
        """Generator for all keys in the store."""
        with self.env.begin(db=self.db) as txn:
            cursor = txn.cursor()
            for k, _ in cursor:
                yield k.decode("utf-8")

    def prefix_scan(self, prefix: str) -> Iterator[tuple[str, Any]]:
        prefix_bytes = prefix.encode("utf-8")
        with self.env.begin(db=self.db) as txn:
            cursor = txn.cursor()
            if cursor.set_range(prefix_bytes):
                for k, v in cursor:
                    if not k.startswith(prefix_bytes):
                        break
                    yield (k.decode("utf-8"), self._deserialize(v))

    def close(self):
        self.env.close()
