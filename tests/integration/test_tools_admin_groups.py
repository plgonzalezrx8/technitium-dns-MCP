from urllib.parse import parse_qs

import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "endpoint", "payload", "response"),
    [
        (
            "dns_list_admin_groups",
            "/api/admin/groups/list",
            {},
            {"groups": [{"name": "admins"}]},
        ),
        (
            "dns_get_admin_group",
            "/api/admin/groups/get",
            {"group": "admins", "include_users": True},
            {"name": "admins", "members": ["alice"]},
        ),
    ],
)
async def test_admin_group_read_tools_call_expected_endpoints(
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

    if response:
        assert result.data == response
    else:
        assert result.structured_content == {}
    request = httpx_mock.get_request()
    assert request is not None
    expected = {"token": ["token-123"]}
    if "group" in payload:
        expected["group"] = [payload["group"]]  # type: ignore[index]
    if "include_users" in payload:
        expected["includeUsers"] = ["true"]
    assert parse_qs(request.content.decode()) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "payload", "message"),
    [
        (
            "dns_create_admin_group",
            {"group": "operators", "confirm": False},
            "confirm=True",
        ),
        (
            "dns_set_admin_group",
            {"group": "operators", "options": {"description": "Ops"}, "confirm": False},
            "confirm=True",
        ),
        (
            "dns_delete_admin_group",
            {"group": "operators", "confirm": False},
            "destructive",
        ),
        (
            "dns_delete_admin_group",
            {"group": "operators", "confirm": True, "acknowledge": "wrong"},
            'acknowledge="admin-groups"',
        ),
    ],
)
async def test_admin_group_mutation_tools_require_expected_confirmation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    tool_name: str,
    payload: dict[str, object],
    message: str,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match=message):
            await client.call_tool(tool_name, payload)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "endpoint", "payload", "expected_params", "response"),
    [
        (
            "dns_create_admin_group",
            "/api/admin/groups/create",
            {
                "group": "operators",
                "description": "Operations team",
                "confirm": True,
                "acknowledge": "admin-groups",
            },
            {
                "group": ["operators"],
                "description": ["Operations team"],
            },
            {"name": "operators", "description": "Operations team"},
        ),
        (
            "dns_set_admin_group",
            "/api/admin/groups/set",
            {
                "group": "operators",
                "options": {
                    "description": "Updated description",
                    "members": "alice,bob",
                },
                "confirm": True,
                "acknowledge": "admin-groups",
            },
            {
                "group": ["operators"],
                "description": ["Updated description"],
                "members": ["alice,bob"],
            },
            {"name": "operators", "description": "Updated description"},
        ),
        (
            "dns_delete_admin_group",
            "/api/admin/groups/delete",
            {
                "group": "operators",
                "confirm": True,
                "acknowledge": "admin-groups",
            },
            {"group": ["operators"]},
            {},
        ),
    ],
)
async def test_admin_group_mutation_tools_post_expected_payloads(
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

    if response:
        assert result.data == response
    else:
        assert result.structured_content == {}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {"token": ["token-123"], **expected_params}
