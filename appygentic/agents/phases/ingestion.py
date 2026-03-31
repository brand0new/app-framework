"""Phase 1 — Ingestion: requirement parsing, context enrichment, DoR validation."""

from google.adk.agents import LlmAgent

from appygentic.config import settings
from appygentic.tools.bpmn import start_bpmn_process, get_bpmn_process_state
from appygentic.tools.neo4j import query_knowledge_graph, store_requirement_context

ingestion_phase = LlmAgent(
    name="ingestion_phase",
    model=settings.specialist_model,
    description=(
        "Ingestion phase agent. Parses incoming API proxy requirements (natural language, "
        "OpenAPI spec, or structured JSON), enriches context from the Neo4j knowledge graph, "
        "validates Definition of Ready (DoR), and initialises the BPMN process instance. "
        "Returns a structured, validated requirement set or requests missing information."
    ),
    instruction="""
You are the Ingestion Phase agent in the Appygentic PM pipeline.

Your responsibilities:
1. Parse the incoming customer requirement (accept text, YAML, JSON, or OpenAPI spec).
2. Extract key attributes: target platform (GCP Apigee X / Azure APIM), API type,
   authentication requirements, backend endpoints, SLAs, and any custom policies.
3. Query the Neo4j knowledge graph for existing APIs, organisational patterns, and
   technology constraints relevant to this request.
4. Validate the Definition of Ready (DoR) — all requirements must have:
   - Clear target platform (GCP or Azure)
   - At least one backend endpoint or OpenAPI spec
   - Authentication mechanism specified
   - Acceptance criteria or SLA targets
5. If DoR validation fails, produce a structured list of missing information and
   set task state to INPUT_REQUIRED. Do NOT proceed to correlation.
6. If DoR passes, start the BPMN process instance and store validated requirements
   in session state under key "validated_requirements".
7. Always include a correlationId in all tool calls.

Return a JSON object with:
  - status: "dor_passed" | "dor_failed"
  - validated_requirements: {...} (if passed)
  - missing_fields: [...] (if failed)
  - bpmn_instance_id: "..." (if passed)
  - context_summary: "..." (knowledge graph findings)
""",
    tools=[
        start_bpmn_process,
        get_bpmn_process_state,
        query_knowledge_graph,
        store_requirement_context,
    ],
)
