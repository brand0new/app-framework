"""ADK FunctionTools for the BPMN Node.js microservice."""

import json
import logging

import httpx
from google.adk.tools import ToolContext

from appygentic.config import settings

logger = logging.getLogger(__name__)

_HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": settings.bpmn_service_api_key,
}


async def start_bpmn_process(
    process_id: str,
    variables: dict,
    tool_context: ToolContext,
) -> str:
    """Start a BPMN business process instance and store the instance ID in session state.

    Args:
        process_id: The BPMN process definition ID (e.g. "api_proxy_workflow").
        variables: Initial process variables to set on the instance.
        tool_context: ADK ToolContext providing session state access.

    Returns:
        JSON string with instanceId and initial state.
    """
    correlation_id = tool_context.state.get("correlationId", "unknown")
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{settings.bpmn_service_url}/process/start",
            json={"processId": process_id, "variables": variables},
            headers={**_HEADERS, "X-Correlation-Id": correlation_id},
        )
        resp.raise_for_status()
        result = resp.json()

    instance_id = result.get("instanceId")
    tool_context.state[f"bpmn_instance_{process_id}"] = instance_id
    logger.info("BPMN process started: %s -> instance %s", process_id, instance_id)
    return json.dumps(result)


async def get_bpmn_process_state(
    process_id: str,
    tool_context: ToolContext,
) -> str:
    """Retrieve the current state of a running BPMN process instance.

    Args:
        process_id: The BPMN process definition ID.
        tool_context: ADK ToolContext for session state lookup.

    Returns:
        JSON string with current state and pending activities.
    """
    instance_id = tool_context.state.get(f"bpmn_instance_{process_id}")
    if not instance_id:
        return json.dumps({"error": f"No BPMN instance found for process '{process_id}'"})

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            f"{settings.bpmn_service_url}/process/{instance_id}/state",
            headers=_HEADERS,
        )
        resp.raise_for_status()
        return json.dumps(resp.json())


async def signal_bpmn_process(
    process_id: str,
    signal_name: str,
    signal_data: dict,
    tool_context: ToolContext,
) -> str:
    """Send a signal to a waiting BPMN process activity.

    Args:
        process_id: The BPMN process definition ID.
        signal_name: Name of the signal to send (e.g. "dor_passed", "execution_complete").
        signal_data: Data payload to attach to the signal.
        tool_context: ADK ToolContext for session state lookup.

    Returns:
        JSON string confirming the signal was delivered.
    """
    instance_id = tool_context.state.get(f"bpmn_instance_{process_id}")
    if not instance_id:
        return json.dumps({"error": f"No BPMN instance found for process '{process_id}'"})

    correlation_id = tool_context.state.get("correlationId", "unknown")
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{settings.bpmn_service_url}/process/{instance_id}/signal",
            json={"signal": signal_name, "data": signal_data},
            headers={**_HEADERS, "X-Correlation-Id": correlation_id},
        )
        resp.raise_for_status()
        return json.dumps(resp.json())


async def get_bpmn_process_variables(
    process_id: str,
    tool_context: ToolContext,
) -> str:
    """Read all process variables from a running BPMN instance.

    Args:
        process_id: The BPMN process definition ID.
        tool_context: ADK ToolContext for session state lookup.

    Returns:
        JSON string with all current process variables.
    """
    instance_id = tool_context.state.get(f"bpmn_instance_{process_id}")
    if not instance_id:
        return json.dumps({"error": f"No BPMN instance found for process '{process_id}'"})

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            f"{settings.bpmn_service_url}/process/{instance_id}/variables",
            headers=_HEADERS,
        )
        resp.raise_for_status()
        return json.dumps(resp.json())
