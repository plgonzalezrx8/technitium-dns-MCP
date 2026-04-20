from urllib.parse import parse_qs

import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
async def test_dns_list_blocked_zones_passes_navigation_params(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/blocked/list",
        json={"status": "ok", "response": {"domain": "example.com", "zones": ["ads.example.com"]}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_list_blocked_zones",
            {"domain": "example.com", "direction": "up"},
        )

    assert result.data == {"domain": "example.com", "zones": ["ads.example.com"]}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "direction": ["up"],
        "domain": ["example.com"],
        "token": ["token-123"],
    }


@pytest.mark.asyncio
async def test_dns_export_blocked_zones_returns_plaintext_content(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/blocked/export",
        content=b"ads.example.com\ntrack.example.com\n",
        headers={
            "content-type": "text/plain",
            "content-disposition": "attachment;filename=BlockedZones.txt",
        },
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool("dns_export_blocked_zones", {})

    assert result.data == {
        "content": "ads.example.com\ntrack.example.com\n",
        "content_type": "text/plain",
        "filename": "BlockedZones.txt",
    }


@pytest.mark.asyncio
async def test_dns_delete_blocked_zone_requires_destructive_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match="destructive"):
            await client.call_tool(
                "dns_delete_blocked_zone",
                {"domain": "example.com", "confirm": False},
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "endpoint", "payload", "expected_params"),
    [
        (
            "dns_add_blocked_zone",
            "/api/blocked/add",
            {"domain": "ads.example.com", "confirm": True},
            {"domain": ["ads.example.com"]},
        ),
        (
            "dns_delete_blocked_zone",
            "/api/blocked/delete",
            {"domain": "ads.example.com", "confirm": True},
            {"domain": ["ads.example.com"]},
        ),
        (
            "dns_flush_blocked_zones",
            "/api/blocked/flush",
            {"confirm": True},
            {},
        ),
        (
            "dns_import_blocked_zones",
            "/api/blocked/import",
            {"zones": ["ads.example.com", "track.example.com"], "confirm": True},
            {"blockedZones": ["ads.example.com,track.example.com"]},
        ),
    ],
)
async def test_blocked_zone_mutation_tools_call_expected_endpoints(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
    *,
    tool_name: str,
    endpoint: str,
    payload: dict[str, object],
    expected_params: dict[str, list[str]],
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")
    httpx_mock.add_response(
        url=f"http://dns.local:5380{endpoint}",
        json={"status": "ok", "response": {"ok": True}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(tool_name, payload)

    assert result.data == {"ok": True}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {"token": ["token-123"], **expected_params}
