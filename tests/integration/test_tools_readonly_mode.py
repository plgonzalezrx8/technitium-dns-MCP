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
        "dns_get_zone_ds_info",
        "dns_get_zone_dnssec_properties",
        "dns_list_cache",
        "dns_list_allowed_zones",
        "dns_export_allowed_zones",
        "dns_list_blocked_zones",
        "dns_export_blocked_zones",
        "dns_list_apps",
        "dns_list_store_apps",
        "dns_get_app_config",
        "dns_resolve_query",
        "dns_get_tsig_key_names",
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
        "dns_sign_zone",
        "dns_unsign_zone",
        "dns_convert_zone_to_nsec",
        "dns_convert_zone_to_nsec3",
        "dns_update_zone_nsec3_parameters",
        "dns_update_zone_dnskey_ttl",
        "dns_add_zone_private_key",
        "dns_update_zone_private_key",
        "dns_delete_zone_private_key",
        "dns_publish_all_zone_private_keys",
        "dns_rollover_zone_dnskey",
        "dns_retire_zone_dnskey",
        "dns_delete_cached_zone",
        "dns_flush_cache",
        "dns_add_allowed_zone",
        "dns_delete_allowed_zone",
        "dns_flush_allowed_zones",
        "dns_import_allowed_zones",
        "dns_add_blocked_zone",
        "dns_delete_blocked_zone",
        "dns_flush_blocked_zones",
        "dns_import_blocked_zones",
        "dns_download_and_install_app",
        "dns_download_and_update_app",
        "dns_install_app",
        "dns_update_app",
        "dns_uninstall_app",
        "dns_set_app_config",
        "dns_set_settings",
        "dns_force_update_block_lists",
        "dns_temporary_disable_blocking",
        "dns_backup_settings",
        "dns_restore_settings",
    }.isdisjoint(tool_names)
