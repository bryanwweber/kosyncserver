import time
from collections.abc import Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

from .logging import Logger, generate_correlation_id

logger: Logger = structlog.get_logger()


class LogCorrelationIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        structlog.contextvars.bind_contextvars(correlation_id=generate_correlation_id())

        await self.app(scope, receive, send)

        structlog.contextvars.unbind_contextvars("correlation_id")


class LogRequestResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        client_ip = request.client.host
        method = request.method
        path = request.url.path
        body = await request.body()

        logger.info(
            "Request started", client_ip=client_ip, method=method, path=path, body=body
        )

        response = await call_next(request)
        chunks = [chunk async for chunk in response.body_iterator]
        resp_body = b"".join(chunks)
        end_time = time.perf_counter()
        duration = end_time - start_time
        logger.info(
            "Request completed",
            status_code=response.status_code,
            client_ip=client_ip,
            method=method,
            path=path,
            body=resp_body,
            duration=duration,
        )

        return Response(
            content=resp_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
