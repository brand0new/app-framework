"""MCP Streamable HTTP server for Apigee X skill tools."""

import io
import json
import re
import zipfile
from typing import Any

from mcp.server import Server
from mcp.server.streamable_http import StreamableHTTPServerTransport
from mcp.types import CallToolResult, TextContent, Tool
from starlette.applications import Starlette
from starlette.routing import Route

server = Server("apigee-skill")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="validate_proxy_xml", description="Validate Apigee proxy XML structure", inputSchema={"type": "object", "properties": {"xml_content": {"type": "string"}}, "required": ["xml_content"]}),
        Tool(name="validate_policy_xml", description="Validate an Apigee policy XML file", inputSchema={"type": "object", "properties": {"policy_type": {"type": "string"}, "xml_content": {"type": "string"}}, "required": ["policy_type", "xml_content"]}),
        Tool(name="lint_proxy_bundle", description="Lint a complete proxy bundle for best-practice violations", inputSchema={"type": "object", "properties": {"bundle_files": {"type": "object"}}, "required": ["bundle_files"]}),
        Tool(name="generate_policy_oauthv2", description="Generate an OAuthV2 policy XML", inputSchema={"type": "object", "properties": {"policy_name": {"type": "string"}, "operation": {"type": "string", "enum": ["VerifyAccessToken", "GenerateAccessToken", "RefreshAccessToken"]}}, "required": ["policy_name", "operation"]}),
        Tool(name="generate_policy_quota", description="Generate a Quota policy XML", inputSchema={"type": "object", "properties": {"policy_name": {"type": "string"}, "count": {"type": "integer"}, "interval": {"type": "integer"}, "time_unit": {"type": "string", "enum": ["minute", "hour", "day", "month"]}}, "required": ["policy_name", "count", "interval", "time_unit"]}),
        Tool(name="generate_policy_spike_arrest", description="Generate a SpikeArrest policy XML", inputSchema={"type": "object", "properties": {"policy_name": {"type": "string"}, "rate": {"type": "string"}}, "required": ["policy_name", "rate"]}),
        Tool(name="package_proxy_bundle", description="Package proxy files into a deployable ZIP bundle", inputSchema={"type": "object", "properties": {"proxy_name": {"type": "string"}, "files": {"type": "object"}}, "required": ["proxy_name", "files"]}),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[Any]:
    if name == "validate_proxy_xml":
        xml = arguments["xml_content"]
        # Basic validation: check for required Apigee proxy elements
        issues = []
        if "<ProxyEndpoint" not in xml:
            issues.append("Missing <ProxyEndpoint> element")
        if "<HTTPProxyConnection>" not in xml:
            issues.append("Missing <HTTPProxyConnection> element")
        result = {"valid": len(issues) == 0, "issues": issues}
        return [TextContent(type="text", text=json.dumps(result))]

    elif name == "validate_policy_xml":
        xml = arguments["xml_content"]
        policy_type = arguments["policy_type"]
        issues = []
        if f"<{policy_type}" not in xml:
            issues.append(f"Missing <{policy_type}> root element")
        if 'name=' not in xml:
            issues.append("Policy element missing 'name' attribute")
        result = {"valid": len(issues) == 0, "issues": issues}
        return [TextContent(type="text", text=json.dumps(result))]

    elif name == "generate_policy_oauthv2":
        name_attr = arguments["policy_name"]
        operation = arguments["operation"]
        xml = f"""<OAuthV2 name="{name_attr}" enabled="true">
  <Operation>{operation}</Operation>
  <ExpiresIn>3600000</ExpiresIn>
  <RefreshTokenExpiresIn>86400000</RefreshTokenExpiresIn>
  <GenerateResponse enabled="true"/>
</OAuthV2>"""
        return [TextContent(type="text", text=xml)]

    elif name == "generate_policy_quota":
        name_attr = arguments["policy_name"]
        count = arguments["count"]
        interval = arguments["interval"]
        time_unit = arguments["time_unit"]
        xml = f"""<Quota name="{name_attr}" type="calendar" enabled="true">
  <Allow countRef="verifyapikey.VerifyAPIKey.apiproduct.developer.quota.limit" count="{count}"/>
  <Interval ref="verifyapikey.VerifyAPIKey.apiproduct.developer.quota.interval">{interval}</Interval>
  <TimeUnit ref="verifyapikey.VerifyAPIKey.apiproduct.developer.quota.timeunit">{time_unit}</TimeUnit>
  <Identifier ref="client_id"/>
  <Distributed>true</Distributed>
  <Synchronous>true</Synchronous>
</Quota>"""
        return [TextContent(type="text", text=xml)]

    elif name == "generate_policy_spike_arrest":
        name_attr = arguments["policy_name"]
        rate = arguments["rate"]
        xml = f"""<SpikeArrest name="{name_attr}" enabled="true">
  <Rate>{rate}</Rate>
  <Identifier ref="client_id"/>
  <UseEffectiveCount>true</UseEffectiveCount>
</SpikeArrest>"""
        return [TextContent(type="text", text=xml)]

    elif name == "package_proxy_bundle":
        proxy_name = arguments["proxy_name"]
        files = arguments["files"]
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path, content in files.items():
                zf.writestr(f"apiproxy/{file_path}", content)
        result = {
            "bundle_name": f"{proxy_name}.zip",
            "file_count": len(files),
            "size_bytes": buf.tell(),
        }
        return [TextContent(type="text", text=json.dumps(result))]

    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


# Build Starlette ASGI app
transport = StreamableHTTPServerTransport(path="/mcp")
app = Starlette(routes=[Route("/mcp", transport.handle_post_request, methods=["POST"])])

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "3100")))
