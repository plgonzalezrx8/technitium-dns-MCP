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


def test_list_endpoints_can_filter_by_classification() -> None:
    from technitium_dns_mcp.client.endpoint_catalog import list_endpoints

    readonly_tools = {endpoint.tool_name for endpoint in list_endpoints(classification="readonly")}

    assert {"dns_get_settings", "dns_list_zones"} <= readonly_tools
    assert "dns_create_primary_zone" not in readonly_tools


def test_get_endpoint_raises_helpful_error_for_unknown_tool() -> None:
    from technitium_dns_mcp.client.endpoint_catalog import get_endpoint

    with pytest.raises(KeyError, match="dns_delete_zone"):
        get_endpoint("dns_delete_zone")
