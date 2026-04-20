from __future__ import annotations

from technitium_dns_mcp.client.models import (
    ConfirmationPolicy,
    EndpointClassification,
    EndpointMetadata,
)

ENDPOINT_CATALOG: tuple[EndpointMetadata, ...] = (
    EndpointMetadata(
        tool_name="dns_get_settings",
        api_path="/api/settings/get",
        family="settings",
        classification="readonly",
    ),
    EndpointMetadata(
        tool_name="dns_list_zones",
        api_path="/api/zones/list",
        family="zones",
        classification="readonly",
    ),
    EndpointMetadata(
        tool_name="dns_create_primary_zone",
        api_path="/api/zones/create",
        family="zones",
        classification="mutation",
        required_params=("zone",),
        confirmation_policy=ConfirmationPolicy(mode="confirm"),
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
