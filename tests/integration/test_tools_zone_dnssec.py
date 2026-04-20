from urllib.parse import parse_qs

import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "endpoint", "payload", "response_key"),
    [
        (
            "dns_get_zone_ds_info",
            "/api/zones/dnssec/viewDS",
            {"zone": "example.com"},
            "dsRecords",
        ),
        (
            "dns_get_zone_dnssec_properties",
            "/api/zones/dnssec/properties/get",
            {"zone": "example.com"},
            "privateKeys",
        ),
    ],
)
async def test_dnssec_read_tools_call_expected_endpoints(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
    *,
    tool_name: str,
    endpoint: str,
    payload: dict[str, object],
    response_key: str,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url=f"http://dns.local:5380{endpoint}",
        json={"status": "ok", "response": {response_key: [{"zone": "example.com"}]}} ,
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(tool_name, payload)

    assert result.data == {response_key: [{"zone": "example.com"}]}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "token": ["token-123"],
        "zone": ["example.com"],
    }


@pytest.mark.asyncio
async def test_dns_unsign_zone_requires_destructive_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match="destructive"):
            await client.call_tool(
                "dns_unsign_zone",
                {"zone": "example.com", "confirm": False},
            )


@pytest.mark.asyncio
async def test_dns_delete_zone_private_key_requires_destructive_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match="destructive"):
            await client.call_tool(
                "dns_delete_zone_private_key",
                {"zone": "example.com", "key_tag": 12345, "confirm": False},
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "endpoint", "payload", "expected_params"),
    [
        (
            "dns_sign_zone",
            "/api/zones/dnssec/sign",
            {
                "zone": "example.com",
                "options": {
                    "algorithm": "RSA",
                    "hashAlgorithm": "SHA256",
                    "kskKeySize": 2048,
                    "zskKeySize": 2048,
                    "nxProof": "NSEC3",
                    "iterations": 5,
                    "saltLength": 8,
                },
                "confirm": True,
            },
            {
                "algorithm": ["RSA"],
                "hashAlgorithm": ["SHA256"],
                "iterations": ["5"],
                "kskKeySize": ["2048"],
                "nxProof": ["NSEC3"],
                "saltLength": ["8"],
                "zskKeySize": ["2048"],
                "zone": ["example.com"],
            },
        ),
        (
            "dns_unsign_zone",
            "/api/zones/dnssec/unsign",
            {"zone": "example.com", "confirm": True},
            {"zone": ["example.com"]},
        ),
        (
            "dns_convert_zone_to_nsec",
            "/api/zones/dnssec/properties/convertToNSEC",
            {"zone": "example.com", "confirm": True},
            {"zone": ["example.com"]},
        ),
        (
            "dns_convert_zone_to_nsec3",
            "/api/zones/dnssec/properties/convertToNSEC3",
            {"zone": "example.com", "iterations": 12, "salt_length": 16, "confirm": True},
            {"iterations": ["12"], "saltLength": ["16"], "zone": ["example.com"]},
        ),
        (
            "dns_update_zone_nsec3_parameters",
            "/api/zones/dnssec/properties/updateNSEC3Params",
            {"zone": "example.com", "iterations": 10, "salt_length": 8, "confirm": True},
            {"iterations": ["10"], "saltLength": ["8"], "zone": ["example.com"]},
        ),
        (
            "dns_update_zone_dnskey_ttl",
            "/api/zones/dnssec/properties/updateDnsKeyTtl",
            {"zone": "example.com", "dnskey_ttl": 3600, "confirm": True},
            {"dnsKeyTtl": ["3600"], "zone": ["example.com"]},
        ),
        (
            "dns_add_zone_private_key",
            "/api/zones/dnssec/properties/addPrivateKey",
            {
                "zone": "example.com",
                "key_data": {
                    "keyType": "ZoneSigningKey",
                    "algorithm": "ED25519",
                    "rolloverDays": 30,
                },
                "confirm": True,
            },
            {
                "algorithm": ["ED25519"],
                "keyType": ["ZoneSigningKey"],
                "rolloverDays": ["30"],
                "zone": ["example.com"],
            },
        ),
        (
            "dns_update_zone_private_key",
            "/api/zones/dnssec/properties/updatePrivateKey",
            {"zone": "example.com", "key_tag": 12345, "rollover_days": 45, "confirm": True},
            {"keyTag": ["12345"], "rolloverDays": ["45"], "zone": ["example.com"]},
        ),
        (
            "dns_delete_zone_private_key",
            "/api/zones/dnssec/properties/deletePrivateKey",
            {"zone": "example.com", "key_tag": 12345, "confirm": True},
            {"keyTag": ["12345"], "zone": ["example.com"]},
        ),
        (
            "dns_publish_all_zone_private_keys",
            "/api/zones/dnssec/properties/publishAllPrivateKeys",
            {"zone": "example.com", "confirm": True},
            {"zone": ["example.com"]},
        ),
        (
            "dns_rollover_zone_dnskey",
            "/api/zones/dnssec/properties/rolloverDnsKey",
            {"zone": "example.com", "key_tag": 12345, "confirm": True},
            {"keyTag": ["12345"], "zone": ["example.com"]},
        ),
        (
            "dns_retire_zone_dnskey",
            "/api/zones/dnssec/properties/retireDnsKey",
            {"zone": "example.com", "key_tag": 12345, "confirm": True},
            {"keyTag": ["12345"], "zone": ["example.com"]},
        ),
    ],
)
async def test_dnssec_mutation_tools_post_expected_payloads(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
    *,
    tool_name: str,
    endpoint: str,
    payload: dict[str, object],
    expected_params: dict[str, list[str]],
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")
    httpx_mock.add_response(
        url=f"http://dns.local:5380{endpoint}",
        json={"status": "ok", "response": {"ok": True}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(tool_name, payload)

    assert result.data == {"ok": True}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "token": ["token-123"],
        **expected_params,
    }
