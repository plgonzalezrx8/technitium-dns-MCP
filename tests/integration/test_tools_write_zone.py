from urllib.parse import parse_qs

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


@pytest.mark.asyncio
async def test_dns_create_zone_calls_api_when_confirmed(
    monkeypatch: pytest.MonkeyPatch, httpx_mock
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/zones/create",
        json={
            "status": "ok",
            "response": {"zone": {"name": "secondary.example.com", "type": "Secondary"}},
        },
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_create_zone",
            {
                "zone": "secondary.example.com",
                "zone_type": "Secondary",
                "options": {"catalog": "default", "disabled": True},
                "confirm": True,
            },
        )

    assert result.data["zone"]["type"] == "Secondary"
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "catalog": ["default"],
        "disabled": ["true"],
        "token": ["token-123"],
        "type": ["Secondary"],
        "zone": ["secondary.example.com"],
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "payload", "endpoint", "expected_params"),
    [
        (
            "dns_clone_zone",
            {"zone": "clone.example.com", "source_zone": "source.example.com", "confirm": True},
            "/api/zones/clone",
            {"sourceZone": ["source.example.com"], "zone": ["clone.example.com"]},
        ),
        (
            "dns_convert_zone",
            {"zone": "example.com", "zone_type": "Stub", "confirm": True},
            "/api/zones/convert",
            {"type": ["Stub"], "zone": ["example.com"]},
        ),
        (
            "dns_enable_zone",
            {"zone": "example.com", "confirm": True},
            "/api/zones/enable",
            {"zone": ["example.com"]},
        ),
        (
            "dns_disable_zone",
            {"zone": "example.com", "confirm": True},
            "/api/zones/disable",
            {"zone": ["example.com"]},
        ),
        (
            "dns_resync_zone",
            {"zone": "example.com", "confirm": True},
            "/api/zones/resync",
            {"zone": ["example.com"]},
        ),
        (
            "dns_set_zone_options",
            {
                "zone": "example.com",
                "options": {"notifyFailed": True, "expiryTtl": 600},
                "confirm": True,
            },
            "/api/zones/options/set",
            {"expiryTtl": ["600"], "notifyFailed": ["true"], "zone": ["example.com"]},
        ),
        (
            "dns_set_zone_permissions",
            {
                "zone": "example.com",
                "user_permissions": [{"name": "alice", "canWrite": True}],
                "group_permissions": [{"name": "dns-admins", "canWrite": True}],
                "confirm": True,
            },
            "/api/zones/permissions/set",
            {
                "groupPermissions": ['[{"name":"dns-admins","canWrite":true}]'],
                "userPermissions": ['[{"name":"alice","canWrite":true}]'],
                "zone": ["example.com"],
            },
        ),
    ],
)
async def test_zone_mutation_tools_post_expected_payloads(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
    *,
    tool_name: str,
    payload: dict[str, object],
    endpoint: str,
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
    assert parse_qs(request.content.decode()) == {
        "token": ["token-123"],
        **expected_params,
    }


@pytest.mark.asyncio
async def test_dns_delete_zone_requires_destructive_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match="destructive"):
            await client.call_tool(
                "dns_delete_zone",
                {"zone": "example.com", "confirm": False},
            )


@pytest.mark.asyncio
async def test_dns_delete_zone_calls_api_when_confirmed(
    monkeypatch: pytest.MonkeyPatch, httpx_mock
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/zones/delete",
        json={"status": "ok", "response": {"deleted": True}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_delete_zone",
            {"zone": "example.com", "confirm": True},
        )

    assert result.data == {"deleted": True}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "token": ["token-123"],
        "zone": ["example.com"],
    }
