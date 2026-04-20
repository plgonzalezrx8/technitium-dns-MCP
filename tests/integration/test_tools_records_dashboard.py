from urllib.parse import parse_qs

import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
async def test_dns_delete_all_stats_requires_destructive_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match="destructive"):
            await client.call_tool("dns_delete_all_stats", {"confirm": False})


@pytest.mark.asyncio
async def test_dns_delete_all_stats_calls_api_when_confirmed(
    monkeypatch: pytest.MonkeyPatch, httpx_mock
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/dashboard/stats/deleteAll",
        json={"status": "ok", "response": {"deleted": True}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool("dns_delete_all_stats", {"confirm": True})

    assert result.data == {"deleted": True}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {"token": ["token-123"]}


@pytest.mark.asyncio
async def test_dns_get_records_returns_zone_records(
    monkeypatch: pytest.MonkeyPatch, httpx_mock
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/zones/records/get",
        json={
            "status": "ok",
            "response": {
                "records": [{"domain": "www.example.com", "type": "A", "ttl": 300}]
            },
        },
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_get_records",
            {"domain": "www.example.com", "zone": "example.com", "list_zone": True},
        )

    assert result.data == {
        "records": [{"domain": "www.example.com", "type": "A", "ttl": 300}]
    }
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "domain": ["www.example.com"],
        "listZone": ["true"],
        "token": ["token-123"],
        "zone": ["example.com"],
    }


@pytest.mark.asyncio
async def test_dns_add_record_requires_confirmation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match="confirm"):
            await client.call_tool(
                "dns_add_record",
                {
                    "domain": "www.example.com",
                    "record_type": "A",
                    "record_data": {"ipAddress": "192.168.1.10"},
                    "confirm": False,
                },
            )


@pytest.mark.asyncio
async def test_dns_add_record_posts_generic_record_params(
    monkeypatch: pytest.MonkeyPatch, httpx_mock
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/zones/records/add",
        json={"status": "ok", "response": {"added": True}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_add_record",
            {
                "domain": "www.example.com",
                "zone": "example.com",
                "record_type": "A",
                "ttl": 300,
                "overwrite": True,
                "comments": "web server",
                "expiry_ttl": 30,
                "record_data": {"ipAddress": "192.168.1.10"},
                "confirm": True,
            },
        )

    assert result.data == {"added": True}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "comments": ["web server"],
        "domain": ["www.example.com"],
        "expiryTtl": ["30"],
        "ipAddress": ["192.168.1.10"],
        "overwrite": ["true"],
        "token": ["token-123"],
        "ttl": ["300"],
        "type": ["A"],
        "zone": ["example.com"],
    }


@pytest.mark.asyncio
async def test_dns_update_record_posts_old_and_new_record_specific_params(
    monkeypatch: pytest.MonkeyPatch, httpx_mock
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/zones/records/update",
        json={"status": "ok", "response": {"updated": True}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_update_record",
            {
                "domain": "www.example.com",
                "zone": "example.com",
                "record_type": "A",
                "new_domain": "api.example.com",
                "ttl": 600,
                "disable": False,
                "comments": "migrated",
                "record_data": {
                    "oldIpAddress": "192.168.1.10",
                    "ipAddress": "192.168.1.20",
                },
                "confirm": True,
            },
        )

    assert result.data == {"updated": True}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "comments": ["migrated"],
        "disable": ["false"],
        "domain": ["www.example.com"],
        "ipAddress": ["192.168.1.20"],
        "newDomain": ["api.example.com"],
        "oldIpAddress": ["192.168.1.10"],
        "token": ["token-123"],
        "ttl": ["600"],
        "type": ["A"],
        "zone": ["example.com"],
    }


@pytest.mark.asyncio
async def test_dns_delete_record_requires_destructive_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match="destructive"):
            await client.call_tool(
                "dns_delete_record",
                {
                    "domain": "www.example.com",
                    "record_type": "A",
                    "record_selector": {"ipAddress": "192.168.1.20"},
                    "confirm": False,
                },
            )


@pytest.mark.asyncio
async def test_dns_delete_record_posts_selector_params_when_confirmed(
    monkeypatch: pytest.MonkeyPatch, httpx_mock
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/zones/records/delete",
        json={"status": "ok", "response": {"deleted": True}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_delete_record",
            {
                "domain": "www.example.com",
                "zone": "example.com",
                "record_type": "A",
                "record_selector": {"ipAddress": "192.168.1.20"},
                "confirm": True,
            },
        )

    assert result.data == {"deleted": True}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "domain": ["www.example.com"],
        "ipAddress": ["192.168.1.20"],
        "token": ["token-123"],
        "type": ["A"],
        "zone": ["example.com"],
    }
