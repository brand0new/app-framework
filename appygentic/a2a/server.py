"""A2A gateway server — exposes the PM agent via A2A v1.0.0 over HTTP."""

import json
import logging
import uuid
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from google.adk.a2a import to_a2a

from appygentic.agents.root import pm_agent
from appygentic.config import settings
from appygentic.observability.otel import configure_otel

logger = logging.getLogger(__name__)

# ── Load Agent Card ───────────────────────────────────────────────────────────

_CARD_PATH = Path(__file__).parent / "agent_card.json"
_agent_card_data: dict = json.loads(_CARD_PATH.read_text())

# Patch the base URL from settings at runtime
_agent_card_data["supportedInterfaces"][0]["url"] = settings.a2a_base_url
_agent_card_data["supportedInterfaces"][1]["url"] = settings.a2a_base_url.rstrip("/") + "/rest"


# ── Build A2A ASGI App ────────────────────────────────────────────────────────

def build_app() -> FastAPI:
    """Construct the FastAPI application with A2A routes and auxiliary endpoints."""
    configure_otel()

    # ADK auto-generates the A2A JSON-RPC and REST routes from the agent
    a2a_asgi = to_a2a(pm_agent, agent_card=_agent_card_data)

    app = FastAPI(
        title="Appygentic A2A Gateway",
        version="2.0.0",
        description="A2A v1.0.0 gateway for the Appygentic PM Agent",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Middleware: inject correlationId into every request ───────────────────

    @app.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-Id") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-Id"] = correlation_id
        return response

    # ── Well-known Agent Card endpoint ────────────────────────────────────────

    @app.get("/.well-known/agent-card.json", include_in_schema=False)
    async def agent_card():
        return Response(
            content=json.dumps(_agent_card_data, indent=2),
            media_type="application/json",
        )

    # ── Health check ──────────────────────────────────────────────────────────

    @app.get("/health", include_in_schema=False)
    async def health():
        return {"status": "ok", "version": "2.0.0"}

    # ── Mount the ADK A2A ASGI app under /a2a ────────────────────────────────

    app.mount("/a2a", a2a_asgi)

    return app


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "appygentic.a2a.server:build_app",
        factory=True,
        host=settings.a2a_gateway_host,
        port=settings.a2a_gateway_port,
        log_level=settings.otel_log_level.lower(),
        reload=False,
    )
