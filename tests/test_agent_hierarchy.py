"""Tests for ADK agent hierarchy construction."""

import pytest
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent


def test_pm_orchestrator_is_sequential_agent():
    from appygentic.agents.root import pm_agent
    assert isinstance(pm_agent, SequentialAgent)
    assert pm_agent.name == "pm_orchestrator"


def test_pm_orchestrator_has_four_phases():
    from appygentic.agents.root import pm_agent
    assert len(pm_agent.sub_agents) == 4


def test_gcp_team_coordinator_is_sequential_agent():
    from appygentic.agents.gcp import gcp_team_coordinator
    assert isinstance(gcp_team_coordinator, SequentialAgent)
    assert gcp_team_coordinator.name == "gcp_apigee_team"


def test_gcp_team_has_parallel_impl_phase():
    from appygentic.agents.gcp import gcp_team_coordinator
    names = [a.name for a in gcp_team_coordinator.sub_agents]
    assert "gcp_parallel_impl" in names


def test_gcp_parallel_impl_has_three_specialists():
    from appygentic.agents.gcp.coordinator import _gcp_parallel_impl
    assert isinstance(_gcp_parallel_impl, ParallelAgent)
    assert len(_gcp_parallel_impl.sub_agents) == 3


def test_azure_team_coordinator_mirrors_gcp_structure():
    from appygentic.agents.azure import azure_team_coordinator
    assert isinstance(azure_team_coordinator, SequentialAgent)
    assert len(azure_team_coordinator.sub_agents) == 4


def test_ingestion_phase_is_llm_agent():
    from appygentic.agents.phases import ingestion_phase
    assert isinstance(ingestion_phase, LlmAgent)
    assert ingestion_phase.name == "ingestion_phase"


def test_delivery_phase_has_billing_tools():
    from appygentic.agents.phases import delivery_phase
    tool_names = [t.__name__ if callable(t) else str(t) for t in delivery_phase.tools]
    assert any("billing" in name or "emit" in name for name in tool_names)


def test_pa_orchestrator_has_five_sub_agents():
    from appygentic.agents.general import pa_orchestrator
    assert len(pa_orchestrator.sub_agents) == 5


def test_business_team_has_four_sub_agents():
    from appygentic.agents.business import business_team
    assert len(business_team.sub_agents) == 4
