"""Azure APIM team coordinator — mirrors GCP structure."""

from google.adk.agents import ParallelAgent, SequentialAgent

from appygentic.agents.azure.specialists import (
    apim_engineer,
    azure_intake_designer,
    azure_skill_optimizer,
    azure_validation_qa,
    function_app_engineer,
    logic_app_engineer,
)

_azure_parallel_impl = ParallelAgent(
    name="azure_parallel_impl",
    description="Implements Logic Apps, Function Apps, and APIM policies in parallel.",
    sub_agents=[
        logic_app_engineer,
        function_app_engineer,
        apim_engineer,
    ],
)

azure_team_coordinator = SequentialAgent(
    name="azure_apim_team",
    description=(
        "Azure APIM implementation team. Executes a sequential pipeline: solution design, "
        "parallel implementation (Logic Apps + Function Apps + APIM policies), QA validation, "
        "and skill optimisation. Produces deployable ARM templates and Azure artifacts."
    ),
    sub_agents=[
        azure_intake_designer,
        _azure_parallel_impl,
        azure_validation_qa,
        azure_skill_optimizer,
    ],
)
