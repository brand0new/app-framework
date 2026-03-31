"""General team specialist agents: Calendar, Email, Research, Planner, Writer."""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHttpParams
from google.adk.tools import google_search

from appygentic.config import settings
from appygentic.tools.bpmn import start_bpmn_process, get_bpmn_process_state
from appygentic.tools.neo4j import query_knowledge_graph

_calendar_toolset = McpToolset(
    connection_params=StreamableHttpParams(url=settings.mcp_calendar_url),
)

_email_toolset = McpToolset(
    connection_params=StreamableHttpParams(url=settings.mcp_email_url),
)

# ── Calendar Agent ────────────────────────────────────────────────────────────

calendar_agent = LlmAgent(
    name="calendar_agent",
    model=settings.primary_model,
    description="Calendar management agent. Handles scheduling, meeting coordination, and time management via MCP calendar tools.",
    instruction="""
You are the Calendar agent. You help with scheduling meetings, managing availability,
setting reminders, and coordinating across time zones.

Use the calendar MCP tools to:
- Check availability before scheduling
- Create calendar events with proper invitees and agendas
- Send meeting invitations
- Manage recurring events
""",
    tools=[_calendar_toolset],
)

# ── Email Agent ───────────────────────────────────────────────────────────────

email_agent = LlmAgent(
    name="email_agent",
    model=settings.primary_model,
    description="Email communications agent. Composes, sends, and manages email communications via MCP email tools.",
    instruction="""
You are the Email agent. You handle professional communications including:
- Composing and sending emails
- Following up on outstanding items
- Summarising email threads
- Managing email templates for common communications

Always maintain a professional tone. Never send emails without explicit instruction.
""",
    tools=[_email_toolset],
)

# ── Research Agent ────────────────────────────────────────────────────────────

research_agent = LlmAgent(
    name="research_agent",
    model=settings.specialist_model,
    description="Research agent. Performs web research and queries the Neo4j knowledge graph to provide comprehensive context and insights.",
    instruction="""
You are the Research agent. You synthesise information from:
1. Google Search — for current information, documentation, and industry trends
2. Neo4j Knowledge Graph — for organisational context, existing API patterns, and historical data

Always cite your sources and distinguish between verified knowledge graph data
and web search results. Flag any conflicting information.
""",
    tools=[google_search, query_knowledge_graph],
)

# ── Planner Agent ─────────────────────────────────────────────────────────────

planner_agent = LlmAgent(
    name="planner_agent",
    model=settings.specialist_model,
    description="Planning agent. Creates BPMN process plans and project timelines for complex multi-step tasks.",
    instruction="""
You are the Planner agent. You create structured plans for complex tasks:
1. Break down work into BPMN-compatible process steps
2. Identify gateways (decision points) and parallel flows
3. Estimate effort and sequence tasks
4. Start BPMN process instances for plan execution tracking

Use BPMN tools to instantiate process definitions when a formal workflow is needed.
""",
    tools=[start_bpmn_process, get_bpmn_process_state],
)

# ── Writer Agent ──────────────────────────────────────────────────────────────

writer_agent = LlmAgent(
    name="writer_agent",
    model=settings.specialist_model,
    description="Technical writer agent. Generates documentation, specifications, proposals, and reports.",
    instruction="""
You are the Writer agent. You produce high-quality technical and business documents:
- API documentation (OpenAPI annotations, developer guides)
- Implementation specifications
- Project status reports
- Business proposals and case studies
- Process documentation

Adapt your writing style to the target audience (technical or business).
Always structure documents clearly with headings, summaries, and action items.
""",
)
