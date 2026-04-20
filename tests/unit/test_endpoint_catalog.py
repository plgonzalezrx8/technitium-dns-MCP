import pytest


def test_get_endpoint_returns_existing_tool_metadata() -> None:
    from technitium_dns_mcp.client.endpoint_catalog import get_endpoint

    endpoint = get_endpoint("dns_create_primary_zone")

    assert endpoint.tool_name == "dns_create_primary_zone"
    assert endpoint.api_path == "/api/zones/create"
    assert endpoint.family == "zones"
    assert endpoint.classification == "mutation"
    assert endpoint.required_params == ("zone",)
    assert endpoint.optional_params == ()
    assert endpoint.confirmation_policy.mode == "confirm"


@pytest.mark.parametrize(
    ("tool_name", "api_path", "classification", "confirmation_mode"),
    [
        ("dns_get_top_stats", "/api/dashboard/stats/getTop", "readonly", "none"),
        (
            "dns_delete_all_stats",
            "/api/dashboard/stats/deleteAll",
            "destructive",
            "destructive",
        ),
        ("dns_list_catalog_zones", "/api/zones/catalogs/list", "readonly", "none"),
        ("dns_create_zone", "/api/zones/create", "mutation", "confirm"),
        ("dns_delete_zone", "/api/zones/delete", "destructive", "destructive"),
        (
            "dns_set_zone_permissions",
            "/api/zones/permissions/set",
            "mutation",
            "confirm",
        ),
        ("dns_get_records", "/api/zones/records/get", "readonly", "none"),
        (
            "dns_delete_record",
            "/api/zones/records/delete",
            "destructive",
            "destructive",
        ),
        ("dns_get_zone_ds_info", "/api/zones/dnssec/viewDS", "readonly", "none"),
        (
            "dns_sign_zone",
            "/api/zones/dnssec/sign",
            "mutation",
            "confirm",
        ),
        (
            "dns_unsign_zone",
            "/api/zones/dnssec/unsign",
            "destructive",
            "destructive",
        ),
        ("dns_list_cache", "/api/cache/list", "readonly", "none"),
        (
            "dns_delete_cached_zone",
            "/api/cache/delete",
            "destructive",
            "destructive",
        ),
        ("dns_export_allowed_zones", "/api/allowed/export", "readonly", "none"),
        ("dns_add_blocked_zone", "/api/blocked/add", "mutation", "confirm"),
        ("dns_list_apps", "/api/apps/list", "readonly", "none"),
        ("dns_install_app", "/api/apps/install", "mutation", "confirm"),
        ("dns_resolve_query", "/api/dnsClient/resolve", "readonly", "none"),
        ("dns_get_tsig_key_names", "/api/settings/getTsigKeyNames", "readonly", "none"),
        ("dns_set_settings", "/api/settings/set", "mutation", "confirm"),
        ("dns_backup_settings", "/api/settings/backup", "admin", "critical"),
        ("dns_restore_settings", "/api/settings/restore", "admin", "critical"),
    ],
)
def test_get_endpoint_covers_phase1_to_phase3_tools(
    *, tool_name: str, api_path: str, classification: str, confirmation_mode: str
) -> None:
    from technitium_dns_mcp.client.endpoint_catalog import get_endpoint

    endpoint = get_endpoint(tool_name)

    assert endpoint.api_path == api_path
    assert endpoint.classification == classification
    assert endpoint.confirmation_policy.mode == confirmation_mode


def test_list_endpoints_can_filter_by_classification() -> None:
    from technitium_dns_mcp.client.endpoint_catalog import list_endpoints

    readonly_tools = {endpoint.tool_name for endpoint in list_endpoints(classification="readonly")}

    assert {
        "dns_get_settings",
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
    } <= readonly_tools
    assert "dns_create_primary_zone" not in readonly_tools
    assert "dns_delete_zone" not in readonly_tools


def test_list_endpoints_can_filter_destructive_tools() -> None:
    from technitium_dns_mcp.client.endpoint_catalog import list_endpoints

    destructive_tools = {
        endpoint.tool_name for endpoint in list_endpoints(classification="destructive")
    }

    assert {
        "dns_delete_all_stats",
        "dns_delete_zone",
        "dns_delete_record",
        "dns_unsign_zone",
        "dns_delete_zone_private_key",
        "dns_delete_cached_zone",
        "dns_flush_cache",
        "dns_delete_allowed_zone",
        "dns_flush_allowed_zones",
        "dns_delete_blocked_zone",
        "dns_flush_blocked_zones",
        "dns_uninstall_app",
    } <= destructive_tools


def test_list_endpoints_can_filter_admin_tools() -> None:
    from technitium_dns_mcp.client.endpoint_catalog import list_endpoints

    admin_tools = {endpoint.tool_name for endpoint in list_endpoints(classification="admin")}

    assert {"dns_backup_settings", "dns_restore_settings"} <= admin_tools


def test_get_endpoint_raises_helpful_error_for_unknown_tool() -> None:
    from technitium_dns_mcp.client.endpoint_catalog import get_endpoint

    with pytest.raises(KeyError, match="dns_unknown_tool"):
        get_endpoint("dns_unknown_tool")
