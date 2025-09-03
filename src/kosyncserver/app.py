from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from .database import dispose_db, get_db
from .documents import router as documents_router
from .logging import Logger
from .logging import configure as configure_logging
from .middleware import LogCorrelationIdMiddleware
from .users import router as users_router

logger: Logger = structlog.get_logger()
configure_logging()

create_table_query = """
BEGIN;
CREATE TABLE IF NOT EXISTS documents
    (document_id TEXT,
     percentage REAL,
     progress TEXT,
     device TEXT,
     device_id TEXT,
     timestamp INTEGER,
     UNIQUE (document_id, device_id));
CREATE TABLE IF NOT EXISTS users
    (username TEXT,
     password TEXT,
     UNIQUE (username));
COMMIT;
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = await get_db()
    await db.executescript(create_table_query)
    yield
    await dispose_db()


app = FastAPI(lifespan=lifespan)
app.include_router(documents_router)
app.include_router(users_router)

app.add_middleware(LogCorrelationIdMiddleware)


@app.get("/")
async def root():
    logger.debug("Hello World!")
    return {"message": "Hello World!"}
