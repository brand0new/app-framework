"""Utility to wrap .claude/skills/ or /skills/ MCP packages as ADK McpToolsets."""

import json
import os
from pathlib import Path

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    StreamableHttpParams,
)
from mcp import StdioServerParameters


def wrap_mcp_skill(skill_dir: str | Path) -> McpToolset:
    """Convert a /skills/<name>/ package into an ADK McpToolset.

    Reads the manifest.json to determine transport mode (stdio vs http),
    then returns an appropriately configured McpToolset.

    Args:
        skill_dir: Path to the skill package directory containing manifest.json.

    Returns:
        Configured McpToolset ready to attach to an LlmAgent.
    """
    skill_dir = Path(skill_dir)
    manifest_path = skill_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest.json found in {skill_dir}")

    manifest = json.loads(manifest_path.read_text())
    server_config = manifest["server"]
    exposed_tools: list[str] | None = manifest.get("exposed_tools")

    if server_config.get("transport") == "http":
        # Resolve environment variable references in URL
        url = os.path.expandvars(server_config["url"])
        params = StreamableHttpParams(url=url)
    else:
        # Stdio transport for local/lightweight skills
        params = StdioConnectionParams(
            server_params=StdioServerParameters(
                command=server_config["command"],
                args=server_config.get("args", []),
                env={**os.environ, **server_config.get("env", {})},
            )
        )

    return McpToolset(
        connection_params=params,
        tool_filter=exposed_tools,
    )


def load_all_skills(skills_root: str | Path = "skills") -> dict[str, McpToolset]:
    """Load all skill packages under the given root directory.

    Args:
        skills_root: Directory containing skill subdirectories.

    Returns:
        Dict mapping skill name → McpToolset.
    """
    skills_root = Path(skills_root)
    toolsets: dict[str, McpToolset] = {}
    for entry in skills_root.iterdir():
        if entry.is_dir() and (entry / "manifest.json").exists():
            try:
                toolsets[entry.name] = wrap_mcp_skill(entry)
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning(
                    "Failed to load skill %s: %s", entry.name, exc
                )
    return toolsets
