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
        ("dns_list_dhcp_leases", "/api/dhcp/leases/list", "readonly", "none"),
        (
            "dns_remove_dhcp_lease",
            "/api/dhcp/leases/remove",
            "destructive",
            "destructive",
        ),
        ("dns_get_dhcp_scope", "/api/dhcp/scopes/get", "readonly", "none"),
        ("dns_set_dhcp_scope", "/api/dhcp/scopes/set", "mutation", "confirm"),
        ("dns_list_admin_sessions", "/api/admin/sessions/list", "readonly", "none"),
        (
            "dns_create_admin_api_token",
            "/api/admin/sessions/createToken",
            "admin",
            "critical",
        ),
        ("dns_list_admin_users", "/api/admin/users/list", "readonly", "none"),
        ("dns_create_admin_user", "/api/admin/users/create", "admin", "critical"),
        ("dns_get_admin_user", "/api/admin/users/get", "readonly", "none"),
        ("dns_set_admin_user", "/api/admin/users/set", "admin", "critical"),
        ("dns_list_admin_groups", "/api/admin/groups/list", "readonly", "none"),
        ("dns_set_admin_group", "/api/admin/groups/set", "admin", "critical"),
        (
            "dns_list_admin_permissions",
            "/api/admin/permissions/list",
            "readonly",
            "none",
        ),
        (
            "dns_set_admin_permission",
            "/api/admin/permissions/set",
            "admin",
            "critical",
        ),
        ("dns_get_cluster_state", "/api/admin/cluster/state", "readonly", "none"),
        ("dns_initialize_cluster", "/api/admin/cluster/init", "admin", "critical"),
        (
            "dns_delete_cluster",
            "/api/admin/cluster/primary/delete",
            "admin",
            "critical",
        ),
        (
            "dns_transfer_cluster_config",
            "/api/admin/cluster/primary/transferConfig",
            "admin",
            "critical",
        ),
        (
            "dns_initialize_and_join_cluster",
            "/api/admin/cluster/initJoin",
            "admin",
            "critical",
        ),
    ],
)
def test_get_endpoint_covers_phase1_to_phase6_tools(
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
        "dns_list_dhcp_leases",
        "dns_list_dhcp_scopes",
        "dns_get_dhcp_scope",
        "dns_list_admin_sessions",
        "dns_list_admin_users",
        "dns_get_admin_user",
        "dns_list_admin_groups",
        "dns_get_admin_group",
        "dns_list_admin_permissions",
        "dns_get_admin_permission",
        "dns_get_cluster_state",
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
        "dns_remove_dhcp_lease",
        "dns_remove_dhcp_reserved_lease",
        "dns_delete_dhcp_scope",
    } <= destructive_tools


def test_list_endpoints_can_filter_admin_tools() -> None:
    from technitium_dns_mcp.client.endpoint_catalog import list_endpoints

    admin_tools = {endpoint.tool_name for endpoint in list_endpoints(classification="admin")}

    assert {
        "dns_backup_settings",
        "dns_restore_settings",
        "dns_create_admin_api_token",
        "dns_delete_admin_session",
        "dns_create_admin_user",
        "dns_set_admin_user",
        "dns_delete_admin_user",
        "dns_create_admin_group",
        "dns_set_admin_group",
        "dns_delete_admin_group",
        "dns_set_admin_permission",
        "dns_initialize_cluster",
        "dns_delete_cluster",
        "dns_join_cluster",
        "dns_remove_cluster_secondary_node",
        "dns_delete_cluster_secondary_node",
        "dns_update_cluster_secondary_node",
        "dns_transfer_cluster_config",
        "dns_set_cluster_options",
        "dns_initialize_and_join_cluster",
        "dns_leave_cluster",
        "dns_notify_cluster",
        "dns_resync_cluster",
        "dns_update_cluster_primary_node",
        "dns_promote_to_cluster_primary",
        "dns_update_cluster_node_ip_addresses",
    } <= admin_tools


def test_get_endpoint_raises_helpful_error_for_unknown_tool() -> None:
    from technitium_dns_mcp.client.endpoint_catalog import get_endpoint

    with pytest.raises(KeyError, match="dns_unknown_tool"):
        get_endpoint("dns_unknown_tool")
