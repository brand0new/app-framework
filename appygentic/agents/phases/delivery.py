"""Phase 4 — Delivery: artifact assembly, billing event, handover."""

from google.adk.agents import LlmAgent

from appygentic.config import settings
from appygentic.tools.bpmn import signal_bpmn_process
from appygentic.tools.billing import emit_billing_event, check_credit_balance
from appygentic.tools.kafka import publish_agent_event

delivery_phase = LlmAgent(
    name="delivery_phase",
    model=settings.primary_model,
    description=(
        "Delivery phase agent. Assembles all implementation artifacts into a deployable ZIP "
        "archive, emits a Stripe billing meter event, signals BPMN process completion, and "
        "produces the final A2A task artifact."
    ),
    instruction="""
You are the Delivery Phase agent in the Appygentic PM pipeline.

Your responsibilities:
1. Read "execution_artifacts" from session state.
2. Assemble artifacts into a structured deliverable:
   - /proxy_bundle/   — Apigee X proxy bundle or Azure ARM templates
   - /policies/       — Platform-specific policy files
   - /tests/          — Test suite and validation results
   - /docs/           — Implementation guide and API documentation
   - DEPLOYMENT.md    — Step-by-step deployment instructions
3. Check customer credit balance before finalising (use check_credit_balance).
4. Emit a "deliverable_completed" billing event to Stripe (emit_billing_event).
5. Signal the BPMN process as COMPLETED.
6. Publish a "task_completed" event to Kafka with full metadata.
7. Return the assembled artifact manifest for A2A response construction.

On any error:
- Do NOT charge credits for failed deliveries.
- Signal BPMN with "delivery_failed" and publish error event to Kafka.

Return:
  - artifact_manifest: {files: [...], total_size_bytes: N, checksum: "..."}
  - billing_event_id: "..."
  - bpmn_completion_status: "completed" | "failed"
""",
    tools=[
        signal_bpmn_process,
        emit_billing_event,
        check_credit_balance,
        publish_agent_event,
    ],
)
