from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response
from loguru import logger
from starlette.background import BackgroundTask

from .database import dispose_db, get_db
from .documents import router as documents_router
from .users import router as users_router

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


def log_info(req_body, res_body, response: Response, request: Request):
    logger.debug(
        "Request: body={req_body}, headers={headers}",
        req_body=req_body,
        headers=dict(request.headers),
    )
    logger.debug(
        "Response: status_code={status_code}, headers={headers}, body={res_body}",
        res_body=res_body,
        headers=dict(response.headers),
        status_code=response.status_code,
    )


@app.middleware("http")
async def log_request(request: Request, call_next):
    req_body = await request.body()
    response = await call_next(request)
    chunks = [chunk async for chunk in response.body_iterator]
    res_body = b"".join(chunks)

    task = BackgroundTask(log_info, req_body, res_body, response, request)
    return Response(
        content=res_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
        background=task,
    )

    return response


@app.get("/")
async def root():
    return {"message": "Hello World!"}
