import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server
from technitium_dns_mcp.client.endpoint_catalog import list_endpoints


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("readonly", "expected_names"),
    [
        (
            True,
            {endpoint.tool_name for endpoint in list_endpoints(classification="readonly")}
            | {"dns_health_check"},
        ),
        (
            False,
            {endpoint.tool_name for endpoint in list_endpoints()} | {"dns_health_check"},
        ),
    ],
)
async def test_live_tool_surface_matches_endpoint_catalog(
    monkeypatch: pytest.MonkeyPatch,
    *,
    readonly: bool,
    expected_names: set[str],
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "true" if readonly else "false")

    async with Client(build_mcp_server()) as client:
        tools = await client.list_tools()

    live_names = {tool.name for tool in tools}

    assert live_names == expected_names
    assert "dns_list_logs" in live_names
    assert "dns_query_logs" in live_names
    if readonly:
        assert "dns_delete_log" not in live_names
        assert "dns_delete_all_logs" not in live_names
    else:
        assert "dns_delete_log" in live_names
        assert "dns_delete_all_logs" in live_names
