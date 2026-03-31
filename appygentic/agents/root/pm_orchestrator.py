"""PM Orchestrator — root SequentialAgent, A2A entry point."""

from google.adk.agents import SequentialAgent

from appygentic.agents.phases import (
    ingestion_phase,
    correlation_phase,
    execution_phase,
    delivery_phase,
)

pm_agent = SequentialAgent(
    name="pm_orchestrator",
    description=(
        "Project Manager agent that orchestrates teams of specialist AI agents to deliver "
        "API proxy implementations on GCP Apigee X or Azure APIM. "
        "Submit requirements in natural language or structured format — the agent team "
        "handles design, implementation, testing, and delivery."
    ),
    sub_agents=[
        ingestion_phase,    # Phase 1: Requirement intake + DoR validation
        correlation_phase,  # Phase 2: Task decomposition + team routing
        execution_phase,    # Phase 3: Parallel team execution + QA
        delivery_phase,     # Phase 4: Deliverable assembly + billing handover
    ],
)
