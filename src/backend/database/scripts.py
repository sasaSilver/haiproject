if __name__ != "__main__":
    exit()

import argparse
import asyncio

from .core import engine
from .models.base import Base

parser = argparse.ArgumentParser(description="Manage database tables")

parser.add_argument(
    "--create", action="store_true", help="Create all tables"
)
parser.add_argument(
    "--drop", action="store_true", help="Drop all tables"
)
parser.add_argument(
    "--recreate", action="store_true", help="Drop all tables and create them again"
)

async def do_with_tables(action: str):
    async with engine.begin() as conn:
        if action == "recreate":
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        elif action == "create":
            await conn.run_sync(Base.metadata.create_all)
        elif action == "drop":
            await conn.run_sync(Base.metadata.drop_all)
        else:
            parser.print_help()
            
args = parser.parse_args()

action = next((arg for arg in ['create', 'drop', 'recreate'] if getattr(args, arg)), None)

if action is None:
    parser.print_help()
    exit()

asyncio.run(do_with_tables(action))
