import pytest
from fastmcp import Client
from pytest_httpx import HTTPXMock


@pytest.mark.asyncio
async def test_dns_list_zones_returns_zone_payload(
    monkeypatch: pytest.MonkeyPatch, httpx_mock: HTTPXMock
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://192.168.1.248:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")

    httpx_mock.add_response(
        url="http://192.168.1.248:5380/api/zones/list",
        json={
            "status": "ok",
            "response": {
                "zones": [
                    {"name": "example.com", "type": "Primary", "disabled": False},
                    {"name": "internal.example.com", "type": "Secondary", "disabled": True},
                ]
            },
        },
    )

    from technitium_dns_mcp.app import build_mcp_server

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool("dns_list_zones", {})

    assert result.data == {
        "zones": [
            {"name": "example.com", "type": "Primary", "disabled": False},
            {"name": "internal.example.com", "type": "Secondary", "disabled": True},
        ]
    }
