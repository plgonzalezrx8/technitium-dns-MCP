import pytest
from fastmcp import Client
from pytest_httpx import HTTPXMock


@pytest.mark.asyncio
async def test_dns_get_settings_uses_technitium_api(
    monkeypatch: pytest.MonkeyPatch, httpx_mock: HTTPXMock
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://192.168.1.248:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")

    httpx_mock.add_response(
        url="http://192.168.1.248:5380/api/settings/get",
        json={"status": "ok", "response": {"version": "14.3", "enableBlocking": True}},
    )

    from technitium_dns_mcp.app import build_mcp_server

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool("dns_get_settings", {})

    assert result.data == {"version": "14.3", "enableBlocking": True}


@pytest.mark.asyncio
async def test_dns_health_check_combines_settings_and_stats(
    monkeypatch: pytest.MonkeyPatch, httpx_mock: HTTPXMock
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://192.168.1.248:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")

    httpx_mock.add_response(
        url="http://192.168.1.248:5380/api/settings/get",
        json={
            "status": "ok",
            "response": {"version": "14.3", "defaultRecordTtl": 3600},
        },
    )
    httpx_mock.add_response(
        url="http://192.168.1.248:5380/api/dashboard/stats/get",
        json={
            "status": "ok",
            "response": {"stats": {"totalQueries": 25, "totalBlocked": 5}},
        },
    )

    from technitium_dns_mcp.app import build_mcp_server

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool("dns_health_check", {})

    assert result.data == {
        "version": "14.3",
        "defaultRecordTtl": 3600,
        "stats": {"totalQueries": 25, "totalBlocked": 5},
    }
