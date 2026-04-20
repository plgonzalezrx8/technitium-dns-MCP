import base64
from urllib.parse import parse_qs

import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
async def test_dns_get_tsig_key_names_returns_names(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/settings/getTsigKeyNames",
        json={"status": "ok", "response": {"tsigKeyNames": ["key-a", "key-b"]}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool("dns_get_tsig_key_names", {})

    assert result.data == {"tsigKeyNames": ["key-a", "key-b"]}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {"token": ["token-123"]}


@pytest.mark.asyncio
async def test_dns_set_settings_posts_passthrough_options_when_confirmed(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/settings/set",
        json={"status": "ok", "response": {"saved": True}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_set_settings",
            {
                "options": {"preferIPv6": True, "defaultRecordTtl": 600},
                "confirm": True,
            },
        )

    assert result.data == {"saved": True}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "defaultRecordTtl": ["600"],
        "preferIPv6": ["true"],
        "token": ["token-123"],
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "endpoint", "payload", "expected_params", "error_match"),
    [
        (
            "dns_force_update_block_lists",
            "/api/settings/forceUpdateBlockLists",
            {"confirm": True},
            {},
            "confirm",
        ),
        (
            "dns_temporary_disable_blocking",
            "/api/settings/temporaryDisableBlocking",
            {"minutes": 30, "confirm": True},
            {"minutes": ["30"]},
            "confirm",
        ),
    ],
)
async def test_settings_mutation_tools_require_confirmation_and_post_expected_params(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
    *,
    tool_name: str,
    endpoint: str,
    payload: dict[str, object],
    expected_params: dict[str, list[str]],
    error_match: str,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    failed_payload = dict(payload)
    failed_payload["confirm"] = False

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match=error_match):
            await client.call_tool(tool_name, failed_payload)

    httpx_mock.add_response(
        url=f"http://dns.local:5380{endpoint}",
        json={"status": "ok", "response": {"ok": True}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(tool_name, payload)

    assert result.data == {"ok": True}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {"token": ["token-123"], **expected_params}


@pytest.mark.asyncio
async def test_dns_backup_settings_requires_critical_acknowledgement_and_returns_archive(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match="backup-settings"):
            await client.call_tool(
                "dns_backup_settings",
                {"confirm": True, "acknowledge": "wrong"},
            )

    httpx_mock.add_response(
        url="http://dns.local:5380/api/settings/backup",
        content=b"PK\x03\x04backup-data",
        headers={
            "content-type": "application/zip",
            "content-disposition": "attachment;filename=example_backup.zip",
        },
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_backup_settings",
            {
                "options": {"dnsSettings": True, "zones": True},
                "confirm": True,
                "acknowledge": "backup-settings",
            },
        )

    assert result.data == {
        "content_base64": base64.b64encode(b"PK\x03\x04backup-data").decode(),
        "content_type": "application/zip",
        "filename": "example_backup.zip",
        "size_bytes": 15,
    }
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "dnsSettings": ["true"],
        "token": ["token-123"],
        "zones": ["true"],
    }


@pytest.mark.asyncio
async def test_dns_restore_settings_requires_critical_acknowledgement_and_uploads_archive(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match="restore-settings"):
            await client.call_tool(
                "dns_restore_settings",
                {
                    "confirm": True,
                    "acknowledge": "backup-settings",
                    "archive_base64": base64.b64encode(b"zip-data").decode(),
                },
            )

    httpx_mock.add_response(
        url="http://dns.local:5380/api/settings/restore",
        json={"status": "ok", "response": {"restored": True}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_restore_settings",
            {
                "options": {"dnsSettings": True, "deleteExistingFiles": True},
                "archive_base64": base64.b64encode(b"zip-data").decode(),
                "filename": "backup.zip",
                "confirm": True,
                "acknowledge": "restore-settings",
            },
        )

    assert result.data == {"restored": True}
    request = httpx_mock.get_request()
    assert request is not None
    assert "multipart/form-data" in request.headers["content-type"]
    assert b'name="token"' in request.content
    assert b'token-123' in request.content
    assert b'name="dnsSettings"' in request.content
    assert b'name="deleteExistingFiles"' in request.content
    assert b'filename="backup.zip"' in request.content
    assert b'zip-data' in request.content
