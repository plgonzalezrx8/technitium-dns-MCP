from __future__ import annotations

from technitium_dns_mcp.client.models import (
    ConfirmationMode,
    ConfirmationPolicy,
    EndpointClassification,
    EndpointMetadata,
)


def _endpoint(
    tool_name: str,
    api_path: str,
    family: str,
    classification: EndpointClassification,
    *,
    required_params: tuple[str, ...] = (),
    optional_params: tuple[str, ...] = (),
    confirmation_mode: ConfirmationMode = "none",
) -> EndpointMetadata:
    return EndpointMetadata(
        tool_name=tool_name,
        api_path=api_path,
        family=family,
        classification=classification,
        required_params=required_params,
        optional_params=optional_params,
        confirmation_policy=ConfirmationPolicy(mode=confirmation_mode),
    )


ENDPOINT_CATALOG: tuple[EndpointMetadata, ...] = (
    _endpoint("dns_get_settings", "/api/settings/get", "settings", "readonly"),
    _endpoint(
        "dns_get_top_stats",
        "/api/dashboard/stats/getTop",
        "dashboard",
        "readonly",
        required_params=("type", "statsType"),
        optional_params=(
            "limit",
            "start",
            "end",
            "noReverseLookup",
            "onlyRateLimitedClients",
            "node",
        ),
    ),
    _endpoint(
        "dns_delete_all_stats",
        "/api/dashboard/stats/deleteAll",
        "dashboard",
        "destructive",
        confirmation_mode="destructive",
    ),
    _endpoint("dns_list_zones", "/api/zones/list", "zones", "readonly"),
    _endpoint("dns_list_catalog_zones", "/api/zones/catalogs/list", "zones", "readonly"),
    _endpoint(
        "dns_get_zone_options",
        "/api/zones/options/get",
        "zones",
        "readonly",
        required_params=("zone",),
        optional_params=(
            "includeAvailableCatalogZoneNames",
            "includeAvailableTsigKeyNames",
        ),
    ),
    _endpoint(
        "dns_set_zone_options",
        "/api/zones/options/set",
        "zones",
        "mutation",
        required_params=("zone",),
        confirmation_mode="confirm",
    ),
    _endpoint(
        "dns_get_zone_permissions",
        "/api/zones/permissions/get",
        "zones",
        "readonly",
        required_params=("zone",),
        optional_params=("includeUsersAndGroups",),
    ),
    _endpoint(
        "dns_set_zone_permissions",
        "/api/zones/permissions/set",
        "zones",
        "mutation",
        required_params=("zone",),
        optional_params=("userPermissions", "groupPermissions"),
        confirmation_mode="confirm",
    ),
    _endpoint(
        "dns_create_primary_zone",
        "/api/zones/create",
        "zones",
        "mutation",
        required_params=("zone",),
        confirmation_mode="confirm",
    ),
    _endpoint(
        "dns_create_zone",
        "/api/zones/create",
        "zones",
        "mutation",
        required_params=("zone", "type"),
        confirmation_mode="confirm",
    ),
    _endpoint(
        "dns_clone_zone",
        "/api/zones/clone",
        "zones",
        "mutation",
        required_params=("zone", "sourceZone"),
        confirmation_mode="confirm",
    ),
    _endpoint(
        "dns_convert_zone",
        "/api/zones/convert",
        "zones",
        "mutation",
        required_params=("zone", "type"),
        confirmation_mode="confirm",
    ),
    _endpoint(
        "dns_enable_zone",
        "/api/zones/enable",
        "zones",
        "mutation",
        required_params=("zone",),
        confirmation_mode="confirm",
    ),
    _endpoint(
        "dns_disable_zone",
        "/api/zones/disable",
        "zones",
        "mutation",
        required_params=("zone",),
        confirmation_mode="confirm",
    ),
    _endpoint(
        "dns_delete_zone",
        "/api/zones/delete",
        "zones",
        "destructive",
        required_params=("zone",),
        confirmation_mode="destructive",
    ),
    _endpoint(
        "dns_resync_zone",
        "/api/zones/resync",
        "zones",
        "mutation",
        required_params=("zone",),
        confirmation_mode="confirm",
    ),
    _endpoint(
        "dns_get_records",
        "/api/zones/records/get",
        "records",
        "readonly",
        required_params=("domain",),
        optional_params=("zone", "listZone"),
    ),
    _endpoint(
        "dns_add_record",
        "/api/zones/records/add",
        "records",
        "mutation",
        required_params=("domain",),
        optional_params=("zone", "type", "ttl", "overwrite", "comments", "expiryTtl"),
        confirmation_mode="confirm",
    ),
    _endpoint(
        "dns_update_record",
        "/api/zones/records/update",
        "records",
        "mutation",
        required_params=("domain",),
        optional_params=(
            "zone",
            "type",
            "newDomain",
            "ttl",
            "disable",
            "comments",
            "expiryTtl",
        ),
        confirmation_mode="confirm",
    ),
    _endpoint(
        "dns_delete_record",
        "/api/zones/records/delete",
        "records",
        "destructive",
        required_params=("domain",),
        optional_params=("zone", "type"),
        confirmation_mode="destructive",
    ),
)

_ENDPOINTS_BY_TOOL = {endpoint.tool_name: endpoint for endpoint in ENDPOINT_CATALOG}


def get_endpoint(tool_name: str) -> EndpointMetadata:
    try:
        return _ENDPOINTS_BY_TOOL[tool_name]
    except KeyError as exc:
        raise KeyError(f"Unknown MCP tool in endpoint catalog: {tool_name}") from exc


def list_endpoints(
    *,
    family: str | None = None,
    classification: EndpointClassification | None = None,
) -> tuple[EndpointMetadata, ...]:
    return tuple(
        endpoint
        for endpoint in ENDPOINT_CATALOG
        if (family is None or endpoint.family == family)
        and (classification is None or endpoint.classification == classification)
    )
