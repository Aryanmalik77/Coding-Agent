import traceback
import sys
from verify_subagent_orchestration import verify_orchestration
import asyncio

async def main():
    try:
        await verify_orchestration()
    except Exception as e:
        print(f"FAILED with Exception: {type(e).__name__}: {e}")
        traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    asyncio.run(main())
