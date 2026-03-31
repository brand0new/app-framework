"""Deploy the Appygentic PM agent to Vertex AI Agent Engine."""

import argparse
import logging

import vertexai
from vertexai import agent_engines

from appygentic.agents.root import pm_agent
from appygentic.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def deploy(display_name: str = "Appygentic PM Orchestrator") -> str:
    """Deploy the PM agent to Vertex AI Agent Engine.

    Args:
        display_name: Human-readable name for the Agent Engine resource.

    Returns:
        The resource name of the deployed Agent Engine.
    """
    vertexai.init(
        project=settings.google_cloud_project,
        location=settings.google_cloud_location,
    )

    logger.info("Deploying PM agent to Vertex AI Agent Engine in %s/%s ...",
                settings.google_cloud_project, settings.google_cloud_location)

    remote_app = agent_engines.create(
        agent_engine=pm_agent,
        display_name=display_name,
        requirements=[
            "google-adk>=1.28.0",
            "a2a-sdk>=1.0.0",
            "httpx>=0.27.0",
            "neo4j>=5.20.0",
            "confluent-kafka>=2.4.0",
            "stripe>=9.0.0",
            "opentelemetry-sdk>=1.25.0",
            "mcp>=1.0.0",
            "python-dotenv>=1.0.1",
        ],
    )

    resource_name = remote_app.resource_name
    logger.info("Agent Engine deployed: %s", resource_name)
    return resource_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy Appygentic to Vertex AI Agent Engine")
    parser.add_argument("--display-name", default="Appygentic PM Orchestrator")
    args = parser.parse_args()
    deploy(display_name=args.display_name)
