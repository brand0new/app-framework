"""Phase 2 — Correlation: task decomposition, dependency analysis, team routing."""

from google.adk.agents import LlmAgent

from appygentic.config import settings
from appygentic.tools.bpmn import signal_bpmn_process, get_bpmn_process_variables
from appygentic.tools.neo4j import query_knowledge_graph
from appygentic.tools.kafka import publish_agent_event

correlation_phase = LlmAgent(
    name="correlation_phase",
    model=settings.specialist_model,
    description=(
        "Correlation phase agent. Decomposes validated requirements into implementation tasks, "
        "performs dependency analysis and risk assessment, assigns tasks to the appropriate "
        "platform team (GCP or Azure), and initialises the execution plan."
    ),
    instruction="""
You are the Correlation Phase agent in the Appygentic PM pipeline.

Your responsibilities:
1. Read "validated_requirements" from session state.
2. Perform task decomposition:
   - Solution design task
   - Implementation tasks (proxy bundle / policies / backend integrations)
   - QA / validation task
   - Documentation task
3. Identify dependencies between tasks and estimate relative complexity.
4. Perform risk assessment: identify potential blockers, ambiguities, or constraints.
5. Route to the correct execution team based on target platform:
   - "gcp" → GCP Apigee X team
   - "azure" → Azure APIM team
   - "both" → parallel execution of both teams
6. Signal the BPMN process with the execution plan.
7. Publish a "task_decomposed" event to Kafka.
8. Store the execution plan in session state under "execution_plan".

Return a JSON object with:
  - team_assignment: "gcp" | "azure" | "both"
  - task_list: [{id, name, dependencies, complexity, assignee}]
  - risk_summary: "..."
  - estimated_credits: <number>
""",
    tools=[
        signal_bpmn_process,
        get_bpmn_process_variables,
        query_knowledge_graph,
        publish_agent_event,
    ],
)
