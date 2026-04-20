import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
async def test_dns_create_primary_zone_requires_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match="confirm"):
            await client.call_tool(
                "dns_create_primary_zone",
                {"zone": "example.com", "confirm": False},
            )


@pytest.mark.asyncio
async def test_dns_create_primary_zone_calls_api_when_confirmed(
    monkeypatch: pytest.MonkeyPatch, httpx_mock
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/zones/create",
        json={
            "status": "ok",
            "response": {"zone": {"name": "example.com", "type": "Primary"}},
        },
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_create_primary_zone",
            {"zone": "example.com", "confirm": True},
        )

    assert result.data["zone"]["name"] == "example.com"
    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "POST"
    assert b"zone=example.com" in request.content
    assert b"type=Primary" in request.content


@pytest.mark.asyncio
async def test_dns_create_primary_zone_validates_zone_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match="zone"):
            await client.call_tool(
                "dns_create_primary_zone",
                {"zone": "bad zone", "confirm": True},
            )
