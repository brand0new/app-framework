"""Tests for BPMN FunctionTools (mocked HTTP)."""

import json
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch


class FakeToolContext:
    def __init__(self, state=None):
        self.state = state or {}


@pytest.mark.asyncio
async def test_start_bpmn_process_stores_instance_id():
    from appygentic.tools.bpmn import start_bpmn_process

    mock_response = MagicMock()
    mock_response.json.return_value = {"instanceId": "test-123", "status": "running"}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        ctx = FakeToolContext({"correlationId": "corr-abc"})
        result = await start_bpmn_process("api_proxy_workflow", {"platform": "gcp"}, ctx)

    data = json.loads(result)
    assert data["instanceId"] == "test-123"
    assert ctx.state["bpmn_instance_api_proxy_workflow"] == "test-123"


@pytest.mark.asyncio
async def test_get_bpmn_process_state_returns_error_when_no_instance():
    from appygentic.tools.bpmn import get_bpmn_process_state

    ctx = FakeToolContext({})
    result = await get_bpmn_process_state("api_proxy_workflow", ctx)
    data = json.loads(result)
    assert "error" in data


@pytest.mark.asyncio
async def test_signal_bpmn_process_returns_error_when_no_instance():
    from appygentic.tools.bpmn import signal_bpmn_process

    ctx = FakeToolContext({})
    result = await signal_bpmn_process("api_proxy_workflow", "dor_passed", {}, ctx)
    data = json.loads(result)
    assert "error" in data
