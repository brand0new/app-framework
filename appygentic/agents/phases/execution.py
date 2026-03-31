"""Phase 3 — Execution: routes to GCP or Azure team coordinator(s)."""

from google.adk.agents import LlmAgent, ParallelAgent

from appygentic.config import settings
from appygentic.agents.gcp.coordinator import gcp_team_coordinator
from appygentic.agents.azure.coordinator import azure_team_coordinator
from appygentic.tools.kafka import publish_agent_event

# Parallel execution when both platforms are targeted
both_platforms_agent = ParallelAgent(
    name="both_platforms_execution",
    description="Executes GCP and Azure implementations in parallel when both are required.",
    sub_agents=[gcp_team_coordinator, azure_team_coordinator],
)

# Router agent decides which sub-agent to delegate to
execution_phase = LlmAgent(
    name="execution_phase",
    model=settings.primary_model,
    description=(
        "Execution phase orchestrator. Reads the execution plan from session state and "
        "delegates to the GCP Apigee X team, the Azure APIM team, or both in parallel. "
        "Monitors progress and surfaces QA results."
    ),
    instruction="""
You are the Execution Phase orchestrator in the Appygentic PM pipeline.

Your responsibilities:
1. Read "execution_plan" from session state.
2. Based on team_assignment:
   - "gcp" → delegate to gcp_apigee_team sub-agent
   - "azure" → delegate to azure_apim_team sub-agent
   - "both" → delegate to both_platforms_execution (parallel)
3. Publish execution_started event to Kafka with correlationId.
4. After teams complete, collect their output artifacts from session state.
5. Publish execution_completed event to Kafka.
6. Store combined artifacts under "execution_artifacts" in session state.

Do NOT attempt to implement the proxy yourself — always delegate to the team sub-agents.
""",
    sub_agents=[gcp_team_coordinator, azure_team_coordinator, both_platforms_agent],
    tools=[publish_agent_event],
)
