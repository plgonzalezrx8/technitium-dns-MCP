from __future__ import annotations

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.client.endpoint_catalog import get_endpoint

LIST_ZONES_ENDPOINT = get_endpoint("dns_list_zones")


def register_zone_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_list_zones() -> dict[str, object]:
        return await client.call_or_throw(LIST_ZONES_ENDPOINT.api_path)
