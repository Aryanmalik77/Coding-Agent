"""Launcher for the Coding Agent Telegram Gateway."""

import asyncio
from pathlib import Path
from loguru import logger
import sys
import os

# Heartbeat interval in seconds
HEARTBEAT_INTERVAL = 60  # 1 minute

def log_sanitizer(record):
    """Truncate extremely long strings in log messages for readability."""
    msg = record["message"]
    # Truncate long URLs or data blobs (anything > 200 chars typical for logs)
    if len(msg) > 300:
        record["message"] = msg[:150] + " ... [TRUNCATED] ... " + msg[-150:]
    return True

# Configure loguru with sanitization
logger.remove() # Clear default
logger.add(sys.stdout, colorize=True, 
           format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", 
           level="INFO", 
           filter=log_sanitizer)
logger.add("telegram_gateway.log", rotation="5 MB", level="DEBUG", filter=log_sanitizer)

from coding_agent.bus.telegram import TelegramInterface

# Fetched from environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "MISSING_TOKEN")
WORKSPACE = r"c:\Users\HP\coding agent\coding agent workspace"

async def heartbeat_loop():
    """Periodic pulse to confirm the gateway is alive."""
    while True:
        logger.info("[GATEWAY-PULSE] System alive and monitoring...")
        await asyncio.sleep(HEARTBEAT_INTERVAL)

async def main():
    print(f"--- Launching Coding Agent Telegram Gateway ---")
    print(f"Bot Token: {BOT_TOKEN[:10]}...")
    logger.info("[BOOT] Initializing Telegram Interface...")
    
    interface = TelegramInterface(BOT_TOKEN, WORKSPACE)
    
    # Start heartbeat in background
    asyncio.create_task(heartbeat_loop())
    
    try:
        await interface.start()
    except KeyboardInterrupt:
        interface.stop()
    except Exception as e:
        logger.exception("[FATAL] Gateway failure:")
        print(f"Gateway failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
