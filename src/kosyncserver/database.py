import aiosqlite

from .config import get_settings

db: aiosqlite.Connection | None = None


async def get_db() -> aiosqlite.Connection:
    global db
    if db is None:
        db = await aiosqlite.connect(get_settings().database_path)
    return db


async def dispose_db() -> None:
    global db
    if db is not None:
        await db.close()
        db = None
