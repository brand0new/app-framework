"""Stripe billing client — credit pack management and webhook handling."""

import json
import logging
import time

import stripe
from fastapi import APIRouter, HTTPException, Request, Response

from appygentic.config import settings
from appygentic.tools.billing import create_credit_grant

logger = logging.getLogger(__name__)

stripe.api_key = settings.stripe_secret_key

# Credit pack definitions: (price_usd_cents, credits, description)
CREDIT_PACKS = {
    "starter": (50_000, 50, "Starter — 50 credits"),
    "growth": (200_000, 250, "Growth — 250 credits (20% discount)"),
    "enterprise": (1_000_000, 1_500, "Enterprise — 1,500 credits (33% discount)"),
}

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/webhook")
async def stripe_webhook(request: Request) -> Response:
    """Handle incoming Stripe webhook events.

    Processes:
    - checkout.session.completed → issue credit grant
    - customer.subscription.deleted → suspend credits
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except (ValueError, stripe.SignatureVerificationError) as exc:
        logger.warning("Invalid Stripe webhook: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        metadata = session.get("metadata", {})
        pack_key = metadata.get("credit_pack", "starter")
        _, credits, _ = CREDIT_PACKS.get(pack_key, CREDIT_PACKS["starter"])
        await create_credit_grant(customer_id=customer_id, credits=credits)
        logger.info("Credit grant issued: %d credits for customer %s", credits, customer_id)

    return Response(status_code=200)


def get_or_create_customer(email: str, name: str) -> str:
    """Find an existing Stripe customer by email or create a new one.

    Args:
        email: Customer email address.
        name: Customer display name.

    Returns:
        Stripe customer ID.
    """
    existing = stripe.Customer.list(email=email, limit=1)
    if existing.data:
        return existing.data[0].id
    customer = stripe.Customer.create(email=email, name=name)
    return customer.id


def create_checkout_session(
    customer_id: str,
    pack_key: str,
    success_url: str,
    cancel_url: str,
) -> str:
    """Create a Stripe Checkout session for a credit pack purchase.

    Args:
        customer_id: Stripe customer ID.
        pack_key: Credit pack key ("starter" | "growth" | "enterprise").
        success_url: Redirect URL on successful payment.
        cancel_url: Redirect URL on cancelled payment.

    Returns:
        Stripe Checkout session URL.
    """
    price_cents, credits, description = CREDIT_PACKS[pack_key]
    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": price_cents,
                    "product_data": {"name": description},
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        metadata={"credit_pack": pack_key, "credits": str(credits)},
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.url
