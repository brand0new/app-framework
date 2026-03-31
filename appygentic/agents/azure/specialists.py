"""Azure APIM team specialist agents."""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHttpParams

from appygentic.config import settings

_apim_toolset = McpToolset(
    connection_params=StreamableHttpParams(url=settings.mcp_apim_url),
)

# ── Intake / Solution Designer ────────────────────────────────────────────────

azure_intake_designer = LlmAgent(
    name="azure_intake_designer",
    model=settings.specialist_model,
    description=(
        "Azure APIM intake and solution designer. Produces a detailed solution architecture "
        "for the API implementation on Azure API Management including APIM policies, "
        "Logic App workflows, and Function App integrations."
    ),
    instruction="""
You are the Azure APIM Solution Designer.

Given the validated requirements, produce:
1. APIM API definition (OpenAPI import or manual definition)
2. Required APIM inbound/outbound/backend/on-error policies
3. Logic App workflows needed for orchestration
4. Azure Function Apps needed for transformation
5. ARM template structure overview
6. Network topology (VNet integration, private endpoints if required)

Store the design under session state key "azure_solution_design".
""",
)

# ── Logic App Engineer ────────────────────────────────────────────────────────

logic_app_engineer = LlmAgent(
    name="logic_app_engineer",
    model=settings.specialist_model,
    description=(
        "Azure Logic App Engineer. Generates Logic App workflow definitions for "
        "orchestration scenarios called from Azure APIM."
    ),
    instruction="""
You are the Azure Logic App Engineer.

Using the Azure solution design, implement Logic App workflows:
1. Workflow JSON definitions (Logic App Standard format)
2. Connection references for required connectors
3. Error handling and retry configurations
4. ARM template fragments for each workflow

Store under session state key "azure_logic_app_files".
""",
    tools=[_apim_toolset],
)

# ── Function App Engineer ─────────────────────────────────────────────────────

function_app_engineer = LlmAgent(
    name="function_app_engineer",
    model=settings.specialist_model,
    description=(
        "Azure Function App Engineer. Generates C# or Python Azure Functions for "
        "backend transformation and validation logic called from APIM or Logic Apps."
    ),
    instruction="""
You are the Azure Function App Engineer.

Using the Azure solution design, implement Azure Functions:
1. Function code (C# or Python, based on requirements)
2. function.json bindings configuration
3. host.json configuration
4. Unit tests
5. ARM template fragment for Function App deployment

Store under session state key "azure_function_files".
""",
    tools=[_apim_toolset],
)

# ── APIM Engineer ─────────────────────────────────────────────────────────────

apim_engineer = LlmAgent(
    name="apim_engineer",
    model=settings.specialist_model,
    description=(
        "Azure APIM Engineer. Generates all APIM policy XML files and the API definition "
        "ARM templates for deployment to Azure API Management."
    ),
    instruction="""
You are the Azure APIM Engineer.

Using the Azure solution design, implement:
1. APIM policy XML for each operation (inbound/outbound/backend/on-error)
2. Named values and backends
3. API version set configuration
4. Full ARM template for the APIM API, operations, and policies
5. Azure CLI deployment script

Policies must follow Azure APIM best practices:
- validate-jwt for OAuth token validation
- rate-limit-by-key for per-subscription throttling
- set-backend-service for backend routing
- return-response for mock responses during testing

Store under session state key "azure_apim_files".
""",
    tools=[_apim_toolset],
)

# ── Validation / QA ───────────────────────────────────────────────────────────

azure_validation_qa = LlmAgent(
    name="azure_validation_qa",
    model=settings.specialist_model,
    description=(
        "Azure APIM validation and QA agent. Validates ARM templates, APIM policies, and "
        "Function App code. Generates an integration test suite."
    ),
    instruction="""
You are the Azure Validation & QA agent.

Validate all Azure implementation artifacts:
1. ARM template syntax and resource dependency validation
2. APIM policy XML schema validation
3. Function App code quality checks
4. Security policy completeness (JWT validation, CORS, rate limiting)
5. Generate a Postman/Newman integration test collection for Azure APIM
6. Generate a test execution report

Store results under session state key "azure_qa_results".
Store test suite under "azure_test_suite".
""",
    tools=[_apim_toolset],
)

# ── Skill Optimizer ───────────────────────────────────────────────────────────

azure_skill_optimizer = LlmAgent(
    name="azure_skill_optimizer",
    model=settings.primary_model,
    description=(
        "Azure skill optimizer. Reviews QA results and applies targeted optimizations to the "
        "Azure implementation: caching, retry policies, policy consolidation."
    ),
    instruction="""
You are the Azure Skill Optimizer.

Review azure_qa_results and all implementation artifacts. Apply optimizations:
1. Add APIM response caching (cache-lookup / cache-store)
2. Tune rate-limit-by-key values
3. Optimize Logic App trigger and action configurations
4. Add distributed tracing headers (W3C TraceContext)
5. Improve developer portal documentation

Document each optimisation with a rationale.
Update the relevant files in session state.
""",
)
