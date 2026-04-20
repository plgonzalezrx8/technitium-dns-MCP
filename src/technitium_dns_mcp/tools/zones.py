from __future__ import annotations

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient


def register_zone_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_list_zones() -> dict[str, object]:
        return await client.call_or_throw("/api/zones/list")
