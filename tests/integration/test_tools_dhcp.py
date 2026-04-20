from urllib.parse import parse_qs

import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "endpoint", "payload", "response"),
    [
        (
            "dns_list_dhcp_leases",
            "/api/dhcp/leases/list",
            {},
            {"leases": [{"scope": "office", "address": "192.168.1.10"}]},
        ),
        (
            "dns_list_dhcp_scopes",
            "/api/dhcp/scopes/list",
            {},
            {"scopes": [{"name": "office", "enabled": True}]},
        ),
        (
            "dns_get_dhcp_scope",
            "/api/dhcp/scopes/get",
            {"name": "office"},
            {"name": "office", "subnetMask": "255.255.255.0"},
        ),
    ],
)
async def test_dhcp_read_tools_call_expected_endpoints(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
    *,
    tool_name: str,
    endpoint: str,
    payload: dict[str, object],
    response: dict[str, object],
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url=f"http://dns.local:5380{endpoint}",
        json={"status": "ok", "response": response},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(tool_name, payload)

    assert result.data == response
    request = httpx_mock.get_request()
    assert request is not None
    expected = {"token": ["token-123"]}
    if "name" in payload:
        expected["name"] = [payload["name"]]  # type: ignore[index]
    assert parse_qs(request.content.decode()) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tool_name",
    [
        "dns_remove_dhcp_lease",
        "dns_remove_dhcp_reserved_lease",
        "dns_delete_dhcp_scope",
    ],
)
async def test_dhcp_destructive_tools_require_confirmation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    tool_name: str,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    payload: dict[str, object] = {"name": "office", "confirm": False}
    if tool_name in {"dns_remove_dhcp_lease", "dns_remove_dhcp_reserved_lease"}:
        payload["hardware_address"] = "AA-BB-CC-DD-EE-FF"

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match="destructive"):
            await client.call_tool(tool_name, payload)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "endpoint", "payload", "expected_params", "response"),
    [
        (
            "dns_set_dhcp_scope",
            "/api/dhcp/scopes/set",
            {
                "name": "office",
                "options": {
                    "startingAddress": "192.168.1.10",
                    "endingAddress": "192.168.1.50",
                    "subnetMask": "255.255.255.0",
                    "dnsServers": "1.1.1.1,1.0.0.1",
                },
                "confirm": True,
            },
            {
                "name": ["office"],
                "startingAddress": ["192.168.1.10"],
                "endingAddress": ["192.168.1.50"],
                "subnetMask": ["255.255.255.0"],
                "dnsServers": ["1.1.1.1,1.0.0.1"],
            },
            {"ok": True},
        ),
        (
            "dns_add_dhcp_reserved_lease",
            "/api/dhcp/scopes/addReservedLease",
            {
                "name": "office",
                "hardware_address": "AA-BB-CC-DD-EE-FF",
                "ip_address": "192.168.1.25",
                "host_name": "printer",
                "comments": "front-office",
                "confirm": True,
            },
            {
                "name": ["office"],
                "hardwareAddress": ["AA-BB-CC-DD-EE-FF"],
                "ipAddress": ["192.168.1.25"],
                "hostName": ["printer"],
                "comments": ["front-office"],
            },
            {"ok": True},
        ),
        (
            "dns_remove_dhcp_reserved_lease",
            "/api/dhcp/scopes/removeReservedLease",
            {
                "name": "office",
                "hardware_address": "AA-BB-CC-DD-EE-FF",
                "confirm": True,
            },
            {"name": ["office"], "hardwareAddress": ["AA-BB-CC-DD-EE-FF"]},
            {"ok": True},
        ),
        (
            "dns_enable_dhcp_scope",
            "/api/dhcp/scopes/enable",
            {"name": "office", "confirm": True},
            {"name": ["office"]},
            {"ok": True},
        ),
        (
            "dns_disable_dhcp_scope",
            "/api/dhcp/scopes/disable",
            {"name": "office", "confirm": True},
            {"name": ["office"]},
            {"ok": True},
        ),
        (
            "dns_delete_dhcp_scope",
            "/api/dhcp/scopes/delete",
            {"name": "office", "confirm": True},
            {"name": ["office"]},
            {"ok": True},
        ),
        (
            "dns_remove_dhcp_lease",
            "/api/dhcp/leases/remove",
            {
                "name": "office",
                "hardware_address": "AA-BB-CC-DD-EE-FF",
                "confirm": True,
            },
            {"name": ["office"], "hardwareAddress": ["AA-BB-CC-DD-EE-FF"]},
            {"ok": True},
        ),
        (
            "dns_convert_dhcp_lease_to_reserved",
            "/api/dhcp/leases/convertToReserved",
            {
                "name": "office",
                "client_identifier": "01-AA-BB-CC-DD-EE-FF",
                "confirm": True,
            },
            {"name": ["office"], "clientIdentifier": ["01-AA-BB-CC-DD-EE-FF"]},
            {"ok": True},
        ),
        (
            "dns_convert_dhcp_lease_to_dynamic",
            "/api/dhcp/leases/convertToDynamic",
            {
                "name": "office",
                "hardware_address": "AA-BB-CC-DD-EE-FF",
                "confirm": True,
            },
            {"name": ["office"], "hardwareAddress": ["AA-BB-CC-DD-EE-FF"]},
            {"ok": True},
        ),
    ],
)
async def test_dhcp_mutation_tools_post_expected_payloads(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
    *,
    tool_name: str,
    endpoint: str,
    payload: dict[str, object],
    expected_params: dict[str, list[str]],
    response: dict[str, object],
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")
    httpx_mock.add_response(
        url=f"http://dns.local:5380{endpoint}",
        json={"status": "ok", "response": response},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(tool_name, payload)

    assert result.data == response
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {"token": ["token-123"], **expected_params}
