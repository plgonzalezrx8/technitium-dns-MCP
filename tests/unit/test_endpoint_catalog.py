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
    ],
)
def test_get_endpoint_covers_phase1_tools(
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
    } <= readonly_tools
    assert "dns_create_primary_zone" not in readonly_tools
    assert "dns_delete_zone" not in readonly_tools


def test_list_endpoints_can_filter_destructive_tools() -> None:
    from technitium_dns_mcp.client.endpoint_catalog import list_endpoints

    destructive_tools = {
        endpoint.tool_name for endpoint in list_endpoints(classification="destructive")
    }

    assert {"dns_delete_all_stats", "dns_delete_zone", "dns_delete_record"} <= destructive_tools


def test_get_endpoint_raises_helpful_error_for_unknown_tool() -> None:
    from technitium_dns_mcp.client.endpoint_catalog import get_endpoint

    with pytest.raises(KeyError, match="dns_unknown_tool"):
        get_endpoint("dns_unknown_tool")
