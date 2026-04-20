import base64
from urllib.parse import parse_qs

import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
async def test_cluster_state_tool_calls_expected_endpoint(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/admin/cluster/state",
        json={"status": "ok", "response": {"clusterInitialized": True}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_get_cluster_state",
            {"include_server_ip_addresses": True},
        )

    assert result.data == {"clusterInitialized": True}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "token": ["token-123"],
        "includeServerIpAddresses": ["true"],
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "payload", "message"),
    [
        (
            "dns_initialize_cluster",
            {
                "cluster_domain": "cluster.example.com",
                "primary_node_ip_addresses": ["192.168.1.10"],
                "confirm": False,
            },
            "confirm=True",
        ),
        (
            "dns_delete_cluster",
            {"confirm": False},
            "destructive",
        ),
        (
            "dns_join_cluster",
            {
                "secondary_node_id": 2,
                "secondary_node_url": "https://node2.example.com:53443",
                "secondary_node_ip_addresses": ["192.168.1.11"],
                "secondary_node_certificate": "cert-value",
                "confirm": True,
                "acknowledge": "wrong",
            },
            'acknowledge="cluster-admin"',
        ),
    ],
)
async def test_cluster_mutation_tools_require_strong_confirmation(
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
            "dns_initialize_cluster",
            "/api/admin/cluster/init",
            {
                "cluster_domain": "cluster.example.com",
                "primary_node_ip_addresses": ["192.168.1.10", "192.168.1.12"],
                "confirm": True,
                "acknowledge": "cluster-admin",
            },
            {
                "clusterDomain": ["cluster.example.com"],
                "primaryNodeIpAddresses": ["192.168.1.10,192.168.1.12"],
            },
            {"clusterInitialized": True},
        ),
        (
            "dns_delete_cluster",
            "/api/admin/cluster/primary/delete",
            {
                "force_delete": True,
                "confirm": True,
                "acknowledge": "cluster-admin",
            },
            {"forceDelete": ["true"]},
            {"clusterInitialized": False},
        ),
        (
            "dns_join_cluster",
            "/api/admin/cluster/primary/join",
            {
                "secondary_node_id": 2,
                "secondary_node_url": "https://node2.example.com:53443",
                "secondary_node_ip_addresses": ["192.168.1.11"],
                "secondary_node_certificate": "cert-value",
                "confirm": True,
                "acknowledge": "cluster-admin",
            },
            {
                "secondaryNodeId": ["2"],
                "secondaryNodeUrl": ["https://node2.example.com:53443"],
                "secondaryNodeIpAddresses": ["192.168.1.11"],
                "secondaryNodeCertificate": ["cert-value"],
            },
            {"clusterInitialized": True},
        ),
        (
            "dns_remove_cluster_secondary_node",
            "/api/admin/cluster/primary/removeSecondary",
            {
                "secondary_node_id": 2,
                "confirm": True,
                "acknowledge": "cluster-admin",
            },
            {"secondaryNodeId": ["2"]},
            {"clusterInitialized": True},
        ),
        (
            "dns_delete_cluster_secondary_node",
            "/api/admin/cluster/primary/deleteSecondary",
            {
                "secondary_node_id": 2,
                "confirm": True,
                "acknowledge": "cluster-admin",
            },
            {"secondaryNodeId": ["2"]},
            {"clusterInitialized": True},
        ),
        (
            "dns_update_cluster_secondary_node",
            "/api/admin/cluster/primary/updateSecondary",
            {
                "secondary_node_id": 2,
                "secondary_node_url": "https://node2.example.com:53443",
                "secondary_node_ip_addresses": ["192.168.1.11", "192.168.1.12"],
                "secondary_node_certificate": "cert-value",
                "confirm": True,
                "acknowledge": "cluster-admin",
            },
            {
                "secondaryNodeId": ["2"],
                "secondaryNodeUrl": ["https://node2.example.com:53443"],
                "secondaryNodeIpAddresses": ["192.168.1.11,192.168.1.12"],
                "secondaryNodeCertificate": ["cert-value"],
            },
            {"clusterInitialized": True},
        ),
        (
            "dns_set_cluster_options",
            "/api/admin/cluster/primary/setOptions",
            {
                "options": {
                    "heartbeatRefreshIntervalSeconds": 60,
                    "configRetryIntervalSeconds": 15,
                },
                "confirm": True,
                "acknowledge": "cluster-admin",
            },
            {
                "heartbeatRefreshIntervalSeconds": ["60"],
                "configRetryIntervalSeconds": ["15"],
            },
            {"clusterInitialized": True},
        ),
        (
            "dns_initialize_and_join_cluster",
            "/api/admin/cluster/initJoin",
            {
                "secondary_node_ip_addresses": ["192.168.1.20"],
                "primary_node_url": "https://primary.example.com:53443",
                "primary_node_username": "admin",
                "primary_node_password": "secret",
                "primary_node_totp": "123456",
                "primary_node_ip_address": "192.168.1.10",
                "ignore_certificate_errors": True,
                "confirm": True,
                "acknowledge": "cluster-admin",
            },
            {
                "secondaryNodeIpAddresses": ["192.168.1.20"],
                "primaryNodeUrl": ["https://primary.example.com:53443"],
                "primaryNodeUsername": ["admin"],
                "primaryNodePassword": ["secret"],
                "primaryNodeTotp": ["123456"],
                "primaryNodeIpAddress": ["192.168.1.10"],
                "ignoreCertificateErrors": ["true"],
            },
            {"clusterInitialized": True},
        ),
        (
            "dns_leave_cluster",
            "/api/admin/cluster/secondary/leave",
            {
                "force_leave": True,
                "confirm": True,
                "acknowledge": "cluster-admin",
            },
            {"forceLeave": ["true"]},
            {"clusterInitialized": False},
        ),
        (
            "dns_notify_cluster",
            "/api/admin/cluster/secondary/notify",
            {
                "primary_node_id": 1,
                "primary_node_url": "https://primary.example.com:53443",
                "primary_node_ip_addresses": ["192.168.1.10"],
                "confirm": True,
                "acknowledge": "cluster-admin",
            },
            {
                "primaryNodeId": ["1"],
                "primaryNodeUrl": ["https://primary.example.com:53443"],
                "primaryNodeIpAddresses": ["192.168.1.10"],
            },
            {},
        ),
        (
            "dns_resync_cluster",
            "/api/admin/cluster/secondary/resync",
            {"confirm": True, "acknowledge": "cluster-admin"},
            {},
            {},
        ),
        (
            "dns_update_cluster_primary_node",
            "/api/admin/cluster/secondary/updatePrimary",
            {
                "primary_node_url": "https://primary.example.com:53443",
                "primary_node_ip_addresses": ["192.168.1.10", "192.168.1.11"],
                "confirm": True,
                "acknowledge": "cluster-admin",
            },
            {
                "primaryNodeUrl": ["https://primary.example.com:53443"],
                "primaryNodeIpAddresses": ["192.168.1.10,192.168.1.11"],
            },
            {"clusterInitialized": True},
        ),
        (
            "dns_promote_to_cluster_primary",
            "/api/admin/cluster/secondary/promote",
            {
                "force_delete_primary": True,
                "confirm": True,
                "acknowledge": "cluster-admin",
            },
            {"forceDeletePrimary": ["true"]},
            {"clusterInitialized": True},
        ),
        (
            "dns_update_cluster_node_ip_addresses",
            "/api/admin/cluster/updateIpAddress",
            {
                "ip_addresses": ["192.168.1.10", "192.168.1.11"],
                "confirm": True,
                "acknowledge": "cluster-admin",
            },
            {"ipAddresses": ["192.168.1.10,192.168.1.11"]},
            {"clusterInitialized": True},
        ),
    ],
)
async def test_cluster_mutation_tools_post_expected_payloads(
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


@pytest.mark.asyncio
async def test_cluster_transfer_config_downloads_binary_content_and_sends_header(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/admin/cluster/primary/transferConfig",
        content=b"PK\x03\x04cluster-config",
        headers={
            "content-type": "application/zip",
            "content-disposition": 'attachment; filename="config.zip"',
        },
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_transfer_cluster_config",
            {
                "include_zones": ["example.com", "example.net"],
                "if_modified_since_rfc2822": "Mon, 21 Apr 2025 10:00:00 GMT",
                "confirm": True,
                "acknowledge": "cluster-admin",
            },
        )

    assert result.data == {
        "content_base64": base64.b64encode(b"PK\x03\x04cluster-config").decode(),
        "content_type": "application/zip",
        "filename": "config.zip",
        "size_bytes": len(b"PK\x03\x04cluster-config"),
    }
    request = httpx_mock.get_request()
    assert request is not None
    assert request.headers["If-Modified-Since"] == "Mon, 21 Apr 2025 10:00:00 GMT"
    assert parse_qs(request.content.decode()) == {
        "token": ["token-123"],
        "includeZones": ["example.com,example.net"],
    }
