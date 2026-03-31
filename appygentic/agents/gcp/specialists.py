"""GCP team specialist agents — imported by coordinator."""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHttpParams

from appygentic.config import settings

# ── Intake / Solution Designer ────────────────────────────────────────────────

gcp_intake_designer = LlmAgent(
    name="gcp_intake_designer",
    model=settings.specialist_model,
    description=(
        "GCP Apigee X intake and solution designer. Produces a detailed solution architecture "
        "for the API proxy implementation including proxy structure, backend connectivity, "
        "traffic management policies, and security controls."
    ),
    instruction="""
You are the GCP Apigee X Solution Designer.

Given the validated requirements from session state, produce:
1. Proxy structure design (basepath, target server, flow hooks)
2. Required Apigee policies (OAuthV2, VerifyAPIKey, Quota, SpikeArrest, JavaScript, etc.)
3. Cloud Functions needed for backend transformation
4. Security controls (mTLS, API key, OAuth 2.0 scopes)
5. Traffic management configuration (rate limiting, caching, retry)
6. A high-level deployment topology diagram (ASCII)

Store the design under session state key "gcp_solution_design".
""",
)

# ── API Proxy Engineer ────────────────────────────────────────────────────────

_apigee_toolset = McpToolset(
    connection_params=StreamableHttpParams(url=settings.mcp_apigee_url),
)

api_proxy_engineer = LlmAgent(
    name="api_proxy_engineer",
    model=settings.specialist_model,
    description=(
        "Apigee X API Proxy Engineer. Generates complete proxy bundle XML files including "
        "the proxy endpoint, target endpoint, and all associated flow configurations."
    ),
    instruction="""
You are the Apigee X API Proxy Engineer.

Using the GCP solution design from session state, implement:
1. apiproxy/proxies/default.xml — ProxyEndpoint with all PreFlow/PostFlow hooks
2. apiproxy/targets/default.xml — TargetEndpoint with backend URL and SSL config
3. apiproxy/<proxy-name>.xml — Proxy descriptor
4. All flow configurations referenced in the design

Use the Apigee MCP tools to validate XML structure.
Store generated files under session state key "gcp_proxy_bundle_files".
""",
    tools=[_apigee_toolset],
)

# ── Cloud Functions Engineer ──────────────────────────────────────────────────

cloud_functions_engineer = LlmAgent(
    name="cloud_functions_engineer",
    model=settings.specialist_model,
    description=(
        "GCP Cloud Functions Engineer. Generates Python or Node.js Cloud Functions for "
        "backend transformation, enrichment, and validation logic called by Apigee X."
    ),
    instruction="""
You are the GCP Cloud Functions Engineer.

Using the GCP solution design from session state, implement:
1. Cloud Functions for any backend transformation logic
2. Requirements.txt / package.json for each function
3. Unit tests for each function
4. Deployment configuration (cloudbuild.yaml or equivalent)

Store under session state key "gcp_cloud_functions_files".
""",
    tools=[_apigee_toolset],
)

# ── Apigee Policy Engineer ────────────────────────────────────────────────────

apigee_policy_engineer = LlmAgent(
    name="apigee_policy_engineer",
    model=settings.specialist_model,
    description=(
        "Apigee Policy Engineer. Generates all Apigee X policy XML files referenced in the "
        "proxy bundle: OAuthV2, VerifyAPIKey, Quota, SpikeArrest, JavaScript, AssignMessage, "
        "ExtractVariables, ServiceCallout, etc."
    ),
    instruction="""
You are the Apigee Policy Engineer.

Using the proxy bundle design, implement all required policy XML files:
1. Security policies (OAuthV2/VerifyAPIKey/HMAC)
2. Traffic management (Quota, SpikeArrest)
3. Mediation policies (AssignMessage, ExtractVariables, JSONtoXML, etc.)
4. Extension policies (JavaScript, ServiceCallout)
5. Error handling policies (RaiseFault)

Each policy file must be a valid, well-formed Apigee X policy XML.
Use the Apigee MCP tools to validate each policy.
Store under session state key "gcp_policy_files".
""",
    tools=[_apigee_toolset],
)

# ── Validation / QA ───────────────────────────────────────────────────────────

gcp_validation_qa = LlmAgent(
    name="gcp_validation_qa",
    model=settings.specialist_model,
    description=(
        "GCP Apigee X validation and QA agent. Validates the complete proxy bundle against "
        "Apigee X best practices, runs static analysis, and generates an integration test suite."
    ),
    instruction="""
You are the GCP Validation & QA agent.

Validate all files produced by the GCP implementation team:
1. XML schema validation for all proxy and policy files
2. Apigee X best-practice checks (no hardcoded credentials, proper error handling, etc.)
3. Security policy completeness check
4. Generate a Postman/Newman integration test collection
5. Generate a test execution report

If critical issues are found, return them with severity ratings (CRITICAL / HIGH / MEDIUM).
Store results under session state key "gcp_qa_results".
Store test suite under "gcp_test_suite".
""",
    tools=[_apigee_toolset],
)

# ── Skill Optimizer ───────────────────────────────────────────────────────────

gcp_skill_optimizer = LlmAgent(
    name="gcp_skill_optimizer",
    model=settings.primary_model,
    description=(
        "GCP skill optimizer. Reviews QA results and applies targeted optimizations to the "
        "proxy bundle: caching improvements, quota tuning, policy consolidation."
    ),
    instruction="""
You are the GCP Skill Optimizer.

Review gcp_qa_results and the full implementation artifacts. Apply optimizations:
1. Add response caching where appropriate (PopulateCache / LookupCache)
2. Tune quota and rate limit values based on requirements
3. Consolidate redundant policy steps
4. Improve error messages for developer experience
5. Add OTel trace context propagation headers

Document each optimisation with a rationale.
Update the relevant files in session state.
""",
)
