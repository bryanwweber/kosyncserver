import time
from typing import Annotated

import aiosqlite
import structlog
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .database import get_db
from .logging import Logger
from .users import get_user

router = APIRouter()
logger: Logger = structlog.get_logger()


class RequestPosition(BaseModel):
    document: str
    percentage: float
    progress: str
    device: str
    device_id: str


def document_to_request_position(
    cursor: aiosqlite.Cursor, row: tuple
) -> RequestPosition:
    fields = [c[0] for c in cursor.description]
    return RequestPosition(**dict(zip(fields, row)))


class ResponsePosition(BaseModel):
    document: str
    timestamp: int


@router.get("/syncs/progress/{document}", response_model=RequestPosition)
async def get_sync_progress(
    document: str,
    db: Annotated[aiosqlite.Connection, Depends(get_db)],
    _: Annotated[None, Depends(get_user)],
):
    select_query = """
    SELECT *
    FROM documents
    WHERE document = :document
    ORDER BY timestamp DESC
    LIMIT 1
    """

    logger.debug("Getting sync progress for document", document=document)
    db.row_factory = document_to_request_position
    result = await db.execute(select_query, {"document": document})
    document = await result.fetchone()
    if not document:
        logger.debug("Document not found")
        return JSONResponse(content={"message": "Document not found!"}, status_code=404)
    logger.debug("Document found", **document.model_dump())
    return document


@router.put("/syncs/progress", response_model=ResponsePosition)
async def update_sync_progress(
    request: RequestPosition,
    db: Annotated[aiosqlite.Connection, Depends(get_db)],
    _: Annotated[None, Depends(get_user)],
):
    now = int(time.time())
    update_query = """
    INSERT INTO documents (
        document, percentage, progress, device, device_id, timestamp
    )
    VALUES (:document, :percentage, :progress, :device, :device_id, :timestamp)
    ON CONFLICT (document, device_id)
    DO UPDATE SET percentage = :percentage, progress = :progress, timestamp = :timestamp
    """

    await db.execute(
        update_query,
        {
            "document": request.document,
            "percentage": request.percentage,
            "progress": request.progress,
            "device": request.device,
            "device_id": request.device_id,
            "timestamp": now,
        },
    )
    await db.commit()
    logger.debug("Sync progress updated for document", **request.model_dump())
    return ResponsePosition(
        document=request.document,
        timestamp=now,
    )
