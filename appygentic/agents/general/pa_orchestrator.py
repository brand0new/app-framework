"""PA Orchestrator — routes non-project requests to the General team."""

from google.adk.agents import LlmAgent

from appygentic.agents.general.specialists import (
    calendar_agent,
    email_agent,
    planner_agent,
    research_agent,
    writer_agent,
)
from appygentic.config import settings

pa_orchestrator = LlmAgent(
    name="pa_orchestrator",
    model=settings.primary_model,
    description=(
        "Personal Assistant orchestrator. Routes non-API-implementation requests to "
        "specialist agents: Calendar (scheduling), Email (communications), Research (web + KG), "
        "Planner (BPMN process planning), and Writer (documentation)."
    ),
    instruction="""
You are the PA Orchestrator. You handle requests that don't require API proxy implementation.

Route to the appropriate specialist:
- Scheduling / calendar requests → calendar_agent
- Email / communication tasks → email_agent
- Research / information gathering → research_agent
- Planning / project management → planner_agent
- Writing / documentation → writer_agent

For requests spanning multiple specialists, coordinate them sequentially.
Do NOT handle API proxy implementation — those go to the PM Orchestrator.
""",
    sub_agents=[
        calendar_agent,
        email_agent,
        research_agent,
        planner_agent,
        writer_agent,
    ],
)
