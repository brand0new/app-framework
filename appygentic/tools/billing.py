"""ADK FunctionTools for Stripe credit-based billing."""

import json
import logging
import time

import stripe
from google.adk.tools import ToolContext

from appygentic.config import settings

logger = logging.getLogger(__name__)

stripe.api_key = settings.stripe_secret_key


async def check_credit_balance(
    customer_id: str,
    required_credits: int,
    tool_context: ToolContext,
) -> str:
    """Check whether a customer has sufficient credits for the requested task.

    Args:
        customer_id: Stripe customer ID.
        required_credits: Number of credits the task will consume.
        tool_context: ADK ToolContext (unused but required by tool signature).

    Returns:
        JSON with {"sufficient": bool, "balance": int, "required": int}.
    """
    try:
        # Retrieve active credit grants for the customer
        grants = stripe.billing.CreditGrant.list(customer=customer_id, limit=100)
        total_balance = sum(
            g.amount.value
            for g in grants.data
            if g.status == "active" and (g.expires_at is None or g.expires_at > time.time())
        )
        sufficient = total_balance >= required_credits
        return json.dumps(
            {"sufficient": sufficient, "balance": total_balance, "required": required_credits}
        )
    except stripe.StripeError as exc:
        logger.error("Stripe credit check failed: %s", exc)
        return json.dumps({"error": str(exc), "sufficient": False})


async def emit_billing_event(
    customer_id: str,
    event_name: str,
    credits_consumed: int,
    task_metadata: dict,
    tool_context: ToolContext,
) -> str:
    """Emit a Stripe Billing Meter event on task completion.

    Args:
        customer_id: Stripe customer ID.
        event_name: Meter event name (e.g. "agent_task_completed").
        credits_consumed: Number of credits to deduct.
        task_metadata: Metadata dimensions (agent_type, task_complexity, platform_target).
        tool_context: ADK ToolContext for correlationId.

    Returns:
        JSON with Stripe meter event ID and timestamp.
    """
    correlation_id = tool_context.state.get("correlationId", "unknown")
    try:
        event = stripe.billing.MeterEvent.create(
            event_name=event_name,
            payload={
                "stripe_customer_id": customer_id,
                "value": str(credits_consumed),
                **{k: str(v) for k, v in task_metadata.items()},
            },
            identifier=correlation_id,
        )
        logger.info(
            "Stripe meter event created: %s for customer %s (%d credits)",
            event.identifier,
            customer_id,
            credits_consumed,
        )
        return json.dumps(
            {
                "billing_event_id": event.identifier,
                "credits_consumed": credits_consumed,
                "timestamp": event.created,
            }
        )
    except stripe.StripeError as exc:
        logger.error("Stripe billing event failed: %s", exc)
        return json.dumps({"error": str(exc), "billing_event_id": None})


async def create_credit_grant(
    customer_id: str,
    credits: int,
    expires_in_days: int = 365,
    tool_context: ToolContext | None = None,
) -> str:
    """Issue a credit grant to a customer (called after purchase).

    Args:
        customer_id: Stripe customer ID.
        credits: Number of credits to grant.
        expires_in_days: Days until the credits expire (default 365).
        tool_context: ADK ToolContext (optional).

    Returns:
        JSON with the created CreditGrant ID.
    """
    expires_at = int(time.time()) + (expires_in_days * 86400)
    try:
        grant = stripe.billing.CreditGrant.create(
            customer=customer_id,
            amount={"type": "monetary", "monetary": {"currency": "usd", "value": credits * 100}},
            applicability_config={"scope": {"price_type": "metered"}},
            expires_at=expires_at,
        )
        return json.dumps({"grant_id": grant.id, "credits": credits, "expires_at": expires_at})
    except stripe.StripeError as exc:
        logger.error("Stripe credit grant failed: %s", exc)
        return json.dumps({"error": str(exc)})
