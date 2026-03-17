
import asyncio
from pathlib import Path
from loguru import logger
import sys
import os

# Configure loguru to write to a log file as well
logger.add("gateway_debug.log", rotation="10 MB")

async def diagnostic():
    try:
        print("Checking imports...")
        from coding_agent.core.agent import CodingAgent
        from coding_agent.bus.telegram import TelegramInterface
        
        WORKSPACE = r"c:\Users\HP\coding agent"
        BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "MISSING_TOKEN")
        
        print("Initializing CodingAgent...")
        agent = CodingAgent(Path(WORKSPACE))
        print("CodingAgent initialized.")
        
        print("Initializing TelegramInterface...")
        interface = TelegramInterface(BOT_TOKEN, WORKSPACE)
        print("TelegramInterface initialized.")
        
        print("Diagnostic complete: Initialization successful.")
    except Exception as e:
        print(f"DIAGNOSTIC FAILED: {e}")
        logger.exception("Diagnostic failed:")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(diagnostic())
