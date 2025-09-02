import aiosqlite

db: aiosqlite.Connection | None = None


async def get_db() -> aiosqlite.Connection:
    global db
    if db is None:
        db = await aiosqlite.connect("/tmp/data.db")
    return db


async def dispose_db() -> None:
    global db
    if db is not None:
        await db.close()
        db = None
