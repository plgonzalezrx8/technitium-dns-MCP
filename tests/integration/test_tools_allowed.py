from urllib.parse import parse_qs

import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
async def test_dns_list_allowed_zones_passes_navigation_params(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/allowed/list",
        json={"status": "ok", "response": {"domain": "example.com", "zones": ["ads.example.com"]}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_list_allowed_zones",
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
async def test_dns_export_allowed_zones_returns_plaintext_content(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/allowed/export",
        content=b"example.com\ninternal.example.com\n",
        headers={
            "content-type": "text/plain",
            "content-disposition": "attachment;filename=AllowedZones.txt",
        },
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool("dns_export_allowed_zones", {})

    assert result.data == {
        "content": "example.com\ninternal.example.com\n",
        "content_type": "text/plain",
        "filename": "AllowedZones.txt",
    }


@pytest.mark.asyncio
async def test_dns_delete_allowed_zone_requires_destructive_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match="destructive"):
            await client.call_tool(
                "dns_delete_allowed_zone",
                {"domain": "example.com", "confirm": False},
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "endpoint", "payload", "expected_params"),
    [
        (
            "dns_add_allowed_zone",
            "/api/allowed/add",
            {"domain": "example.com", "confirm": True},
            {"domain": ["example.com"]},
        ),
        (
            "dns_delete_allowed_zone",
            "/api/allowed/delete",
            {"domain": "example.com", "confirm": True},
            {"domain": ["example.com"]},
        ),
        (
            "dns_flush_allowed_zones",
            "/api/allowed/flush",
            {"confirm": True},
            {},
        ),
        (
            "dns_import_allowed_zones",
            "/api/allowed/import",
            {"zones": ["example.com", "internal.example.com"], "confirm": True},
            {"allowedZones": ["example.com,internal.example.com"]},
        ),
    ],
)
async def test_allowed_zone_mutation_tools_call_expected_endpoints(
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
