"""GCP Apigee X team coordinator — SequentialAgent with parallel implementation phase."""

from google.adk.agents import ParallelAgent, SequentialAgent

from appygentic.agents.gcp.specialists import (
    api_proxy_engineer,
    apigee_policy_engineer,
    cloud_functions_engineer,
    gcp_intake_designer,
    gcp_skill_optimizer,
    gcp_validation_qa,
)

# Parallel implementation: proxy bundle + functions + policies run concurrently
_gcp_parallel_impl = ParallelAgent(
    name="gcp_parallel_impl",
    description="Implements proxy bundle, Cloud Functions, and Apigee policies in parallel.",
    sub_agents=[
        api_proxy_engineer,
        cloud_functions_engineer,
        apigee_policy_engineer,
    ],
)

# Full GCP pipeline: design → parallel impl → QA → optimize
gcp_team_coordinator = SequentialAgent(
    name="gcp_apigee_team",
    description=(
        "GCP Apigee X implementation team. Executes a sequential pipeline: solution design, "
        "parallel implementation (proxy bundle + Cloud Functions + policies), QA validation, "
        "and skill optimisation. Produces a deployable Apigee X proxy bundle."
    ),
    sub_agents=[
        gcp_intake_designer,   # Step 1: Solution architecture
        _gcp_parallel_impl,    # Step 2: Parallel implementation
        gcp_validation_qa,     # Step 3: QA + test generation
        gcp_skill_optimizer,   # Step 4: Post-QA optimisation
    ],
)
