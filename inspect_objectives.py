from coding_agent.swarm.lmdb_store import LMDBStore
from pathlib import Path
import json

workspace = Path('c:/Users/HP/coding agent')
store = LMDBStore(workspace)
keys = [k for k in store.list_keys() if k.startswith('fortress:objective:')]
print(f"Total Objectives: {len(keys)}")
for k in keys:
    data = store.get(k)
    print(f"{k} | Title: {data.get('title')}")
