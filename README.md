# Appygentic — ADK-Native Multi-Agent Platform

> **v2.0.0** — Google ADK v1.28.0 · A2A v1.0.0 · Vertex AI Agent Engine · Stripe Billing

Appygentic is a commercially deployable, protocol-compliant AI agent platform that orchestrates 24+ specialist agents to deliver API proxy implementations on **GCP Apigee X** or **Azure APIM** — from natural-language requirements through to deployable artifacts.

---

## Architecture Overview

```
Customer  ──A2A v1.0.0──▶  PM Agent (SequentialAgent, root)
                               │
               ┌───────────────┼───────────────────────┐
               ▼               ▼                       ▼
        Ingestion Phase  Correlation Phase       Execution Phase
        (DoR Validation) (Task Decomposition)    (Team Routing)
                                                       │
                              ┌────────────────────────┤
                              ▼                        ▼
                       GCP Apigee X Team        Azure APIM Team
                       (SequentialAgent)        (SequentialAgent)
                              │                        │
                    ┌─────────┴───────┐     ┌─────────┴───────┐
                    ▼         ▼       ▼     ▼         ▼       ▼
                 Proxy    Functions Policy  Logic   Function  APIM
               Engineer  Engineer  Eng.   Apps      Apps     Eng.
                              │                        │
                              └──────────┬─────────────┘
                                         ▼
                                  Delivery Phase
                                  (Artifact + Billing)
```

**Supporting Infrastructure**

| Component | Technology | Deployment |
|-----------|-----------|------------|
| Agent Runtime | Google ADK v1.28.0 | Vertex AI Agent Engine |
| Agent Protocol | A2A v1.0.0 (JSON-RPC + HTTP/JSON) | Cloud Run |
| Process Engine | bpmn-engine v25.0.1 | Cloud Run |
| MCP Skills | Streamable HTTP servers | Cloud Run |
| Knowledge Graph | Neo4j AuraDB | Managed |
| Event Bus | Confluent Cloud (Kafka) | Managed |
| Billing | Stripe Metered Billing + Credit Grants | Managed |
| Observability | OpenTelemetry + GCP Cloud Trace | Managed |

---

## Agent Hierarchy (24 Agents)

### Root
- **PM Orchestrator** — `SequentialAgent` — A2A entry point, 4-phase pipeline

### General / PA Team
- **PA Orchestrator** — routes non-project requests
- **Calendar**, **Email**, **Research**, **Planner**, **Writer** — specialist LlmAgents

### GCP Apigee X Team
- **Intake/Solution Designer** — architecture and design
- **API Proxy Engineer**, **Cloud Functions Engineer**, **Apigee Policy Engineer** — parallel implementation
- **Validation/QA**, **Skill Optimizer** — quality and performance

### Azure APIM Team
- **Intake/Solution Designer** — architecture and design
- **Logic App Engineer**, **Function App Engineer**, **APIM Engineer** — parallel implementation
- **Validation/QA**, **Skill Optimizer** — quality and performance

### Business Team
- **Marketing**, **Sales**, **Office Management**, **HR**

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Google Cloud project with Vertex AI enabled
- Neo4j AuraDB instance
- Confluent Cloud cluster
- Stripe account

### Local Development

```bash
# 1. Clone and set up Python environment
git clone https://github.com/brand0new/app-framework
cd app-framework
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Start the BPMN microservice
cd bpmn_service && npm install && npm start &
cd ..

# 4. Start the A2A gateway
python -m appygentic.main
```

The A2A gateway starts on `http://localhost:8080`. The Agent Card is available at:
```
http://localhost:8080/.well-known/agent-card.json
```

### Docker Compose

```bash
docker compose up --build
```

### Tests

```bash
pytest tests/ -v
```

---

## A2A Integration

Send a task to the PM agent via A2A JSON-RPC:

```bash
curl -X POST http://localhost:8080/a2a \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{
          "text": "Implement an API proxy on GCP Apigee X for our payments service. Backend: https://payments.internal/v2. OAuth 2.0 auth required. 1000 req/min quota."
        }]
      }
    },
    "id": "req-001"
  }'
```

Stream progress via SSE:
```
POST /a2a  →  method: message/stream
```

---

## Billing — Credit Packs

| Pack | Price | Credits | Use Case |
|------|-------|---------|----------|
| Starter | $500 | 50 | 1–5 API proxy implementations |
| Growth | $2,000 | 250 | Team / department-level usage |
| Enterprise | $10,000 | 1,500 | Enterprise platform integrations |

Credits consumed per task:
- Simple proxy (no transformation): ~10 credits
- Standard proxy (policies + auth): ~20 credits
- Complex proxy (transformation + Cloud Functions): ~40–50 credits

---

## Deployment

### Vertex AI Agent Engine

```bash
python deploy/vertex_ai/deploy.py --display-name "Appygentic PM Orchestrator"
```

### Cloud Run (A2A Gateway + BPMN Service)

```bash
# Build and push images
gcloud builds submit --tag gcr.io/PROJECT_ID/appygentic-a2a-gateway .
gcloud builds submit --tag gcr.io/PROJECT_ID/appygentic-bpmn-service ./bpmn_service

# Deploy services
gcloud run services replace deploy/cloud_run/a2a_gateway.yaml --region us-central1
gcloud run services replace deploy/cloud_run/bpmn_service.yaml --region us-central1
```

---

## Migration Roadmap

| Phase | Weeks | Milestone |
|-------|-------|-----------|
| 1 — Foundation | 1–6 | PM agent + GCP team end-to-end on ADK |
| 2 — A2A + full migration | 7–12 | All 24 agents, A2A SSE streaming |
| 3 — Commercialisation | 13–18 | Stripe billing, first paying customer |
| 4 — Production hardening | 19–24 | 100+ concurrent tasks, <2% failure rate |
| 5 — ADK 2.0 evaluation | 25–30 | Graph-based workflow assessment |

---

## Key Risks

| Risk | Mitigation |
|------|-----------|
| ADK 2.0 breaking changes | Pin to ADK 1.28.0; isolate 2.0 in Phase 5 |
| LiteLLM supply chain (March 2026) | Use Gemini native integration; verify checksums |
| BPMN-ADK state sync | `correlationId` threading; BPMN authoritative for process state |
| MCP lifecycle on Agent Engine | Migrate high-traffic skills to Streamable HTTP on Cloud Run |

---

## Technology Decisions

- **ADK v1.28.0** over ADK 2.0 Alpha — stable, production-ready, all required primitives
- **A2A v1.0.0 as sole protocol** — ACP merged into A2A (August 2025); no separate ACP layer needed
- **BPMN as microservice** — preserves existing JS stack, zero regression risk vs. SpiffWorkflow rewrite
- **ADK AutoFlow** replaces TF-IDF — LLM-driven delegation, semantically richer, no retraining
- **Gemini 2.5 Flash** primary, **Gemini 2.5 Pro** for specialist tasks
- **Stripe credit-based billing** first — fastest path to revenue; GCP/Azure Marketplace in phases 2–3
