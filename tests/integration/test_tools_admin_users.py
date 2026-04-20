from urllib.parse import parse_qs

import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "endpoint", "payload", "response"),
    [
        (
            "dns_list_admin_users",
            "/api/admin/users/list",
            {},
            {"users": [{"username": "alice"}]},
        ),
        (
            "dns_get_admin_user",
            "/api/admin/users/get",
            {"user": "alice", "include_groups": True},
            {"username": "alice", "memberOfGroups": ["admins"]},
        ),
    ],
)
async def test_admin_user_read_tools_call_expected_endpoints(
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
    if "user" in payload:
        expected["user"] = [payload["user"]]  # type: ignore[index]
    if "include_groups" in payload:
        expected["includeGroups"] = ["true"]
    assert parse_qs(request.content.decode()) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "payload", "message"),
    [
        (
            "dns_create_admin_user",
            {"user": "alice", "password": "secret", "confirm": False},
            "confirm=True",
        ),
        (
            "dns_set_admin_user",
            {"user": "alice", "options": {"displayName": "Alice"}, "confirm": False},
            "confirm=True",
        ),
        (
            "dns_delete_admin_user",
            {"user": "alice", "confirm": False},
            "destructive",
        ),
        (
            "dns_delete_admin_user",
            {"user": "alice", "confirm": True, "acknowledge": "wrong"},
            'acknowledge="admin-users"',
        ),
    ],
)
async def test_admin_user_mutation_tools_require_expected_confirmation(
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
            "dns_create_admin_user",
            "/api/admin/users/create",
            {
                "user": "alice",
                "password": "secret",
                "display_name": "Alice Example",
                "confirm": True,
                "acknowledge": "admin-users",
            },
            {
                "user": ["alice"],
                "pass": ["secret"],
                "displayName": ["Alice Example"],
            },
            {"username": "alice", "displayName": "Alice Example"},
        ),
        (
            "dns_set_admin_user",
            "/api/admin/users/set",
            {
                "user": "alice",
                "options": {
                    "displayName": "Alice Updated",
                    "disabled": True,
                    "memberOfGroups": "admins,operators",
                },
                "confirm": True,
                "acknowledge": "admin-users",
            },
            {
                "user": ["alice"],
                "displayName": ["Alice Updated"],
                "disabled": ["true"],
                "memberOfGroups": ["admins,operators"],
            },
            {"username": "alice", "displayName": "Alice Updated"},
        ),
        (
            "dns_delete_admin_user",
            "/api/admin/users/delete",
            {
                "user": "alice",
                "confirm": True,
                "acknowledge": "admin-users",
            },
            {"user": ["alice"]},
            {},
        ),
    ],
)
async def test_admin_user_mutation_tools_post_expected_payloads(
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
