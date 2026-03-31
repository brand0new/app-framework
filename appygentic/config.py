"""Centralised configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Google Cloud
    google_cloud_project: str = ""
    google_cloud_location: str = "us-central1"

    # LLM models
    primary_model: str = "gemini-2.5-flash"
    specialist_model: str = "gemini-2.5-pro"

    # BPMN microservice
    bpmn_service_url: str = "http://localhost:3001"
    bpmn_service_api_key: str = ""

    # Neo4j
    neo4j_uri: str = ""
    neo4j_username: str = "neo4j"
    neo4j_password: str = ""
    neo4j_database: str = "neo4j"

    # Kafka
    kafka_bootstrap_servers: str = ""
    kafka_api_key: str = ""
    kafka_api_secret: str = ""
    kafka_topic_agent_events: str = "appygentic.agent.events"
    kafka_topic_billing_events: str = "appygentic.billing.events"

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_meter_task_completed: str = ""
    stripe_meter_deliverable_accepted: str = ""

    # A2A
    a2a_base_url: str = "http://localhost:8080/a2a"
    a2a_gateway_host: str = "0.0.0.0"
    a2a_gateway_port: int = 8080

    # MCP skill service URLs
    mcp_apigee_url: str = "http://localhost:3100"
    mcp_apim_url: str = "http://localhost:3101"
    mcp_neo4j_url: str = "http://localhost:3102"
    mcp_calendar_url: str = "http://localhost:3103"
    mcp_email_url: str = "http://localhost:3104"

    # OTel
    otel_service_name: str = "appygentic"
    otel_log_level: str = "INFO"


settings = Settings()
