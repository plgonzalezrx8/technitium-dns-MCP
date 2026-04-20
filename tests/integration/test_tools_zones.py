from urllib.parse import parse_qs

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


@pytest.mark.asyncio
async def test_dns_list_catalog_zones_returns_catalog_payload(
    monkeypatch: pytest.MonkeyPatch, httpx_mock: HTTPXMock
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://192.168.1.248:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")

    httpx_mock.add_response(
        url="http://192.168.1.248:5380/api/zones/catalogs/list",
        json={
            "status": "ok",
            "response": {
                "catalogZones": [
                    {"name": "corp.example", "zone": "corp.example.com"},
                    {"name": "edge.example", "zone": "edge.example.com"},
                ]
            },
        },
    )

    from technitium_dns_mcp.app import build_mcp_server

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool("dns_list_catalog_zones", {})

    assert result.data == {
        "catalogZones": [
            {"name": "corp.example", "zone": "corp.example.com"},
            {"name": "edge.example", "zone": "edge.example.com"},
        ]
    }


@pytest.mark.asyncio
async def test_dns_get_zone_options_serializes_optional_flags(
    monkeypatch: pytest.MonkeyPatch, httpx_mock: HTTPXMock
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://192.168.1.248:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")

    httpx_mock.add_response(
        url="http://192.168.1.248:5380/api/zones/options/get",
        json={
            "status": "ok",
            "response": {"zone": "example.com", "notifyFailed": True},
        },
    )

    from technitium_dns_mcp.app import build_mcp_server

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_get_zone_options",
            {
                "zone": "example.com",
                "include_available_catalog_zone_names": True,
                "include_available_tsig_key_names": False,
            },
        )

    assert result.data == {"zone": "example.com", "notifyFailed": True}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "includeAvailableCatalogZoneNames": ["true"],
        "includeAvailableTsigKeyNames": ["false"],
        "token": ["token-123"],
        "zone": ["example.com"],
    }


@pytest.mark.asyncio
async def test_dns_get_zone_permissions_can_include_users_and_groups(
    monkeypatch: pytest.MonkeyPatch, httpx_mock: HTTPXMock
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://192.168.1.248:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")

    httpx_mock.add_response(
        url="http://192.168.1.248:5380/api/zones/permissions/get",
        json={
            "status": "ok",
            "response": {"zone": "example.com", "userPermissions": [{"name": "alice"}]},
        },
    )

    from technitium_dns_mcp.app import build_mcp_server

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_get_zone_permissions",
            {"zone": "example.com", "include_users_and_groups": True},
        )

    assert result.data == {"zone": "example.com", "userPermissions": [{"name": "alice"}]}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "includeUsersAndGroups": ["true"],
        "token": ["token-123"],
        "zone": ["example.com"],
    }
