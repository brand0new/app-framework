"""ADK FunctionTools for Confluent Cloud (Kafka) event publishing."""

import json
import logging
import time

from confluent_kafka import Producer
from google.adk.tools import ToolContext

from appygentic.config import settings

logger = logging.getLogger(__name__)

_producer: Producer | None = None


def _get_producer() -> Producer:
    global _producer
    if _producer is None:
        _producer = Producer(
            {
                "bootstrap.servers": settings.kafka_bootstrap_servers,
                "sasl.mechanism": "PLAIN",
                "security.protocol": "SASL_SSL",
                "sasl.username": settings.kafka_api_key,
                "sasl.password": settings.kafka_api_secret,
            }
        )
    return _producer


def _delivery_report(err, msg):
    if err:
        logger.error("Kafka delivery failed: %s", err)
    else:
        logger.debug("Kafka delivered to %s [%d]", msg.topic(), msg.partition())


async def publish_agent_event(
    event_type: str,
    event_data: dict,
    tool_context: ToolContext,
) -> str:
    """Publish an agent lifecycle event to the Confluent Cloud Kafka topic.

    Args:
        event_type: Event type string (e.g. "task_decomposed", "execution_started").
        event_data: Event payload dictionary.
        tool_context: ADK ToolContext for correlationId and session metadata.

    Returns:
        JSON string confirming the event was queued.
    """
    correlation_id = tool_context.state.get("correlationId", "unknown")
    payload = {
        "eventType": event_type,
        "correlationId": correlation_id,
        "timestamp": int(time.time() * 1000),
        "data": event_data,
    }
    producer = _get_producer()
    producer.produce(
        topic=settings.kafka_topic_agent_events,
        key=correlation_id.encode(),
        value=json.dumps(payload).encode(),
        callback=_delivery_report,
    )
    producer.poll(0)  # trigger delivery callbacks without blocking
    return json.dumps({"queued": True, "eventType": event_type, "correlationId": correlation_id})


async def publish_billing_event(
    event_type: str,
    billing_data: dict,
    tool_context: ToolContext,
) -> str:
    """Publish a billing event to the dedicated billing Kafka topic.

    Args:
        event_type: Billing event type (e.g. "credits_consumed", "task_completed").
        billing_data: Billing metadata (credits, task_id, customer_id, etc.).
        tool_context: ADK ToolContext for correlationId.

    Returns:
        JSON string confirming the event was queued.
    """
    correlation_id = tool_context.state.get("correlationId", "unknown")
    payload = {
        "eventType": event_type,
        "correlationId": correlation_id,
        "timestamp": int(time.time() * 1000),
        "billing": billing_data,
    }
    producer = _get_producer()
    producer.produce(
        topic=settings.kafka_topic_billing_events,
        key=correlation_id.encode(),
        value=json.dumps(payload).encode(),
        callback=_delivery_report,
    )
    producer.poll(0)
    return json.dumps({"queued": True, "eventType": event_type})
