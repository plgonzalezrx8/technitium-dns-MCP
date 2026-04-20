from urllib.parse import parse_qs

import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
async def test_dns_resolve_query_calls_dns_client_endpoint_without_import_support(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/dnsClient/resolve",
        json={"status": "ok", "response": {"response": {"rcode": "NoError"}}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_resolve_query",
            {
                "server": "this-server",
                "domain": "example.com",
                "query_type": "A",
                "protocol": "Udp",
                "dnssec": True,
                "edns_client_subnet": "192.0.2.0/24",
            },
        )

    assert result.data == {"response": {"rcode": "NoError"}}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "dnssec": ["true"],
        "domain": ["example.com"],
        "eDnsClientSubnet": ["192.0.2.0/24"],
        "protocol": ["Udp"],
        "server": ["this-server"],
        "token": ["token-123"],
        "type": ["A"],
    }
