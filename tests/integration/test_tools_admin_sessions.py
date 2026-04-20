from urllib.parse import parse_qs

import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
async def test_admin_sessions_list_tool_calls_expected_endpoint(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/admin/sessions/list",
        json={"status": "ok", "response": {"sessions": [{"username": "admin"}]}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool("dns_list_admin_sessions", {})

    assert result.data == {"sessions": [{"username": "admin"}]}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {"token": ["token-123"]}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "payload", "message"),
    [
        (
            "dns_create_admin_api_token",
            {"user": "alice", "token_name": "cli-token", "confirm": False},
            "confirm=True",
        ),
        (
            "dns_create_admin_api_token",
            {
                "user": "alice",
                "token_name": "cli-token",
                "confirm": True,
                "acknowledge": "wrong",
            },
            'acknowledge="admin-sessions"',
        ),
        (
            "dns_delete_admin_session",
            {"partial_token": "abcd", "confirm": False},
            "destructive",
        ),
        (
            "dns_delete_admin_session",
            {"partial_token": "abcd", "confirm": True, "acknowledge": "wrong"},
            'acknowledge="admin-sessions"',
        ),
    ],
)
async def test_admin_session_mutation_tools_require_strong_confirmation(
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
            "dns_create_admin_api_token",
            "/api/admin/sessions/createToken",
            {
                "user": "alice",
                "token_name": "cli-token",
                "confirm": True,
                "acknowledge": "admin-sessions",
            },
            {"user": ["alice"], "tokenName": ["cli-token"]},
            {"username": "alice", "tokenName": "cli-token", "token": "secret"},
        ),
        (
            "dns_delete_admin_session",
            "/api/admin/sessions/delete",
            {
                "partial_token": "abcd",
                "confirm": True,
                "acknowledge": "admin-sessions",
            },
            {"partialToken": ["abcd"]},
            {},
        ),
    ],
)
async def test_admin_session_mutation_tools_post_expected_payloads(
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
