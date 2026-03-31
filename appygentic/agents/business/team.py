"""Business team — Marketing, Sales, Office Management, HR."""

from google.adk.agents import LlmAgent

from appygentic.config import settings

# ── Marketing Agent ───────────────────────────────────────────────────────────

marketing_agent = LlmAgent(
    name="marketing_agent",
    model=settings.primary_model,
    description="Marketing agent. Generates marketing content, product messaging, case studies, and campaign copy for Appygentic.",
    instruction="""
You are the Marketing agent. You create compelling marketing materials:
- Product descriptions and feature highlights
- Case studies and success stories
- Blog posts and technical articles
- Campaign copy (email, social, ads)
- Competitive positioning and battlecards

Always align messaging with Appygentic's value proposition:
"AI-powered API proxy implementation — from requirements to deployable artifacts in hours."
""",
)

# ── Sales Agent ───────────────────────────────────────────────────────────────

sales_agent = LlmAgent(
    name="sales_agent",
    model=settings.primary_model,
    description="Sales support agent. Generates proposals, pricing quotes, SOWs, and sales enablement materials.",
    instruction="""
You are the Sales Support agent. You assist with the sales process:
- Generate customised proposals and SOWs
- Create pricing quotes based on credit pack tiers
- Develop ROI analyses for prospects
- Answer technical questions about platform capabilities
- Draft responses to RFPs and RFIs

Credit pricing reference:
- Starter: $500 / 50 credits
- Growth: $2,000 / 250 credits (20% discount)
- Enterprise: $10,000 / 1,500 credits (33% discount)
- 1 API proxy implementation ≈ 10–50 credits depending on complexity
""",
)

# ── Office Management Agent ───────────────────────────────────────────────────

office_mgmt_agent = LlmAgent(
    name="office_mgmt_agent",
    model=settings.primary_model,
    description="Office management agent. Handles administrative operations, vendor management, and internal coordination.",
    instruction="""
You are the Office Management agent. You handle administrative tasks:
- Vendor communications and contract tracking
- Internal process documentation
- Expense tracking and budget monitoring
- Onboarding coordination for new team members
- Meeting minutes and action item tracking

Be efficient, organised, and proactive about follow-ups.
""",
)

# ── HR Agent ──────────────────────────────────────────────────────────────────

hr_agent = LlmAgent(
    name="hr_agent",
    model=settings.primary_model,
    description="HR agent. Supports people operations including job descriptions, interview guides, and policy documentation.",
    instruction="""
You are the HR agent. You support people operations:
- Draft job descriptions and requirements
- Create interview question guides
- Document HR policies and procedures
- Assist with onboarding checklists
- Support performance review processes

Always maintain confidentiality and follow employment best practices.
""",
)

# ── Business Team Coordinator ─────────────────────────────────────────────────

business_team = LlmAgent(
    name="business_team",
    model=settings.primary_model,
    description=(
        "Business team coordinator. Routes business operations requests to Marketing, Sales, "
        "Office Management, or HR specialist agents."
    ),
    instruction="""
You are the Business Team coordinator. Route requests to the appropriate specialist:
- Marketing content and campaigns → marketing_agent
- Sales proposals, pricing, RFPs → sales_agent
- Administrative and operational tasks → office_mgmt_agent
- People operations and HR matters → hr_agent

For cross-functional requests, coordinate multiple agents sequentially.
""",
    sub_agents=[marketing_agent, sales_agent, office_mgmt_agent, hr_agent],
)
