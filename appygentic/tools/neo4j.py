"""ADK FunctionTools for Neo4j AuraDB knowledge graph queries."""

import json
import logging
from typing import Any

from neo4j import AsyncGraphDatabase
from google.adk.tools import ToolContext

from appygentic.config import settings

logger = logging.getLogger(__name__)


def _get_driver():
    return AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )


async def query_knowledge_graph(
    cypher_query: str,
    parameters: dict | None = None,
    tool_context: ToolContext | None = None,
) -> str:
    """Execute a read-only Cypher query against the Neo4j knowledge graph.

    Args:
        cypher_query: A Cypher MATCH/RETURN query (no mutations).
        parameters: Optional query parameters dict.
        tool_context: ADK ToolContext (unused but required by tool signature).

    Returns:
        JSON string with query results (list of record dicts).
    """
    params = parameters or {}
    driver = _get_driver()
    try:
        async with driver.session(database=settings.neo4j_database) as session:
            result = await session.run(cypher_query, params)
            records: list[dict[str, Any]] = []
            async for record in result:
                records.append(dict(record))
        return json.dumps({"results": records, "count": len(records)})
    except Exception as exc:
        logger.error("Neo4j query failed: %s", exc)
        return json.dumps({"error": str(exc), "results": []})
    finally:
        await driver.close()


async def store_requirement_context(
    requirement_id: str,
    context_data: dict,
    tool_context: ToolContext | None = None,
) -> str:
    """Persist validated requirement context to the Neo4j knowledge graph.

    Args:
        requirement_id: Unique identifier for this requirement engagement.
        context_data: Validated requirement metadata to persist.
        tool_context: ADK ToolContext (unused but required by tool signature).

    Returns:
        JSON string confirming the write.
    """
    driver = _get_driver()
    try:
        async with driver.session(database=settings.neo4j_database) as session:
            cypher = """
            MERGE (r:Requirement {id: $id})
            SET r += $props, r.updatedAt = datetime()
            RETURN r.id AS id
            """
            result = await session.run(cypher, {"id": requirement_id, "props": context_data})
            record = await result.single()
        return json.dumps({"stored": True, "id": record["id"] if record else requirement_id})
    except Exception as exc:
        logger.error("Neo4j write failed: %s", exc)
        return json.dumps({"error": str(exc), "stored": False})
    finally:
        await driver.close()
