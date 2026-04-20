from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.guards import require_mutation_confirmation
from technitium_dns_mcp.validation import validate_zone_name


def register_zone_mutation_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_create_primary_zone(
        zone: str, confirm: bool = False
    ) -> dict[str, Any]:
        """Create a primary zone after explicit confirmation."""

        require_mutation_confirmation(confirm=confirm)
        safe_zone = validate_zone_name(zone)
        return await client.call_or_throw(
            "/api/zones/create", {"zone": safe_zone, "type": "Primary"}
        )
