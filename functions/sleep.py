import asyncio
from os import getenv


async def sleep(time):
    """Disable sleep if DEBUG env var is set"""
    if not getenv("DEBUG"):
        await asyncio.sleep(time)
