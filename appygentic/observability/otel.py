"""OpenTelemetry configuration with GenAI SemConv v1.37 agent spans."""

import logging

from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from appygentic.config import settings

logger = logging.getLogger(__name__)

_configured = False


def configure_otel() -> None:
    """Initialise the OpenTelemetry SDK with GCP Cloud Trace export.

    Idempotent — safe to call multiple times.
    """
    global _configured
    if _configured:
        return

    resource = Resource.create({SERVICE_NAME: settings.otel_service_name})

    provider = TracerProvider(resource=resource)

    # Export to GCP Cloud Trace (uses ADC for auth)
    try:
        exporter = CloudTraceSpanExporter(project_id=settings.google_cloud_project)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        logger.info("OTel → GCP Cloud Trace exporter configured for project %s",
                    settings.google_cloud_project)
    except Exception as exc:
        logger.warning("Cloud Trace exporter unavailable (%s), traces will not be exported", exc)

    trace.set_tracer_provider(provider)

    # Auto-instrument HTTPX (covers all BPMN service + Neo4j HTTP calls)
    HTTPXClientInstrumentor().instrument()

    _configured = True
    logger.info("OpenTelemetry configured: service=%s", settings.otel_service_name)


def get_tracer(name: str = "appygentic") -> trace.Tracer:
    """Return a named tracer for manual span creation."""
    return trace.get_tracer(name)
