import time
from typing import Annotated

import aiosqlite
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel

from .database import get_db
from .users import get_user

router = APIRouter()


class RequestPosition(BaseModel):
    document_id: str
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
    document_id: str
    timestamp: int


select_query = """
SELECT *
FROM documents
WHERE document_id = :document_id
ORDER BY timestamp DESC
LIMIT 1
"""


@router.get("/syncs/progress/{document_id}", response_model=RequestPosition)
async def get_sync_progress(
    document_id: str,
    db: Annotated[aiosqlite.Connection, Depends(get_db)],
    _: Annotated[None, Depends(get_user)],
):
    logger.debug("Getting sync progress for {document_id}", document_id=document_id)
    db.row_factory = document_to_request_position
    result = await db.execute(select_query, {"document_id": document_id})
    document = await result.fetchone()
    if document:
        return document
    else:
        return JSONResponse(content={"message": "Document not found!"}, status_code=404)


update_query = """
INSERT INTO documents (document_id, percentage, progress, device, device_id, timestamp)
VALUES (:document_id, :percentage, :progress, :device, :device_id, :timestamp)
ON CONFLICT (document_id, device_id)
DO UPDATE SET percentage = :percentage, progress = :progress, timestamp = :timestamp
"""


@router.put("/syncs/progress", response_model=ResponsePosition)
async def update_sync_progress(
    request: RequestPosition,
    db: Annotated[aiosqlite.Connection, Depends(get_db)],
    _: Annotated[None, Depends(get_user)],
):
    now = int(time.time())
    await db.execute(
        update_query,
        {
            "document_id": request.document_id,
            "percentage": request.percentage,
            "progress": request.progress,
            "device": request.device,
            "device_id": request.device_id,
            "timestamp": now,
        },
    )
    await db.commit()
    return ResponsePosition(
        document_id=request.document_id,
        timestamp=now,
    )
