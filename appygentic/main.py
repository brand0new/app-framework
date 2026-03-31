"""Application entry point — starts the A2A gateway."""

import uvicorn

from appygentic.a2a.server import build_app
from appygentic.config import settings

app = build_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.a2a_gateway_host,
        port=settings.a2a_gateway_port,
        log_level=settings.otel_log_level.lower(),
    )
