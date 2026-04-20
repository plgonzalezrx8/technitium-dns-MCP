import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
async def test_readonly_mode_hides_write_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "true")

    async with Client(build_mcp_server()) as client:
        tools = await client.list_tools()

    tool_names = {tool.name for tool in tools}

    assert {
        "dns_get_settings",
        "dns_health_check",
        "dns_get_top_stats",
        "dns_list_zones",
        "dns_list_catalog_zones",
        "dns_get_zone_options",
        "dns_get_zone_permissions",
        "dns_get_records",
    } <= tool_names

    assert {
        "dns_create_primary_zone",
        "dns_delete_all_stats",
        "dns_create_zone",
        "dns_clone_zone",
        "dns_convert_zone",
        "dns_enable_zone",
        "dns_disable_zone",
        "dns_delete_zone",
        "dns_resync_zone",
        "dns_set_zone_options",
        "dns_set_zone_permissions",
        "dns_add_record",
        "dns_update_record",
        "dns_delete_record",
    }.isdisjoint(tool_names)
