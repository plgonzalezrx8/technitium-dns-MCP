from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.client.endpoint_catalog import get_endpoint
from technitium_dns_mcp.validation import normalize_name, normalize_optional_name

RESOLVE_QUERY_ENDPOINT = get_endpoint("dns_resolve_query")


def register_dns_client_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_resolve_query(
        server: str,
        domain: str,
        query_type: str,
        protocol: str | None = None,
        dnssec: bool | None = None,
        edns_client_subnet: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "server": normalize_name(server, field_name="server"),
            "domain": normalize_name(domain, field_name="domain"),
            "type": normalize_name(query_type, field_name="query_type"),
            "protocol": normalize_optional_name(protocol, field_name="protocol"),
            "dnssec": dnssec,
            "eDnsClientSubnet": normalize_optional_name(
                edns_client_subnet,
                field_name="edns_client_subnet",
            ),
        }
        return await client.call_or_throw(RESOLVE_QUERY_ENDPOINT.api_path, params)
