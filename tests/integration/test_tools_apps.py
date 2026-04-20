import base64
from urllib.parse import parse_qs

import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "endpoint", "payload", "response"),
    [
        (
            "dns_list_apps",
            "/api/apps/list",
            {},
            {"apps": [{"name": "sample-app", "version": "1.0.0"}]},
        ),
        (
            "dns_list_store_apps",
            "/api/apps/listStoreApps",
            {},
            {"storeApps": [{"name": "sample-app", "version": "1.1.0"}]},
        ),
        (
            "dns_get_app_config",
            "/api/apps/config/get",
            {"name": "sample-app"},
            {"config": '{"enabled":true}'},
        ),
    ],
)
async def test_app_read_tools_call_expected_endpoints(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
    *,
    tool_name: str,
    endpoint: str,
    payload: dict[str, object],
    response: dict[str, object],
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url=f"http://dns.local:5380{endpoint}",
        json={"status": "ok", "response": response},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(tool_name, payload)

    assert result.data == response
    request = httpx_mock.get_request()
    assert request is not None
    expected = {"token": ["token-123"]}
    if "name" in payload:
        expected["name"] = [payload["name"]]  # type: ignore[index]
    assert parse_qs(request.content.decode()) == expected


@pytest.mark.asyncio
async def test_dns_uninstall_app_requires_destructive_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match="destructive"):
            await client.call_tool(
                "dns_uninstall_app",
                {"name": "sample-app", "confirm": False},
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "endpoint", "payload", "expected_params", "response_key"),
    [
        (
            "dns_download_and_install_app",
            "/api/apps/downloadAndInstall",
            {
                "name": "sample-app",
                "url": "https://store.example/apps/sample-app.zip",
                "confirm": True,
            },
            {"name": ["sample-app"], "url": ["https://store.example/apps/sample-app.zip"]},
            "installedApp",
        ),
        (
            "dns_download_and_update_app",
            "/api/apps/downloadAndUpdate",
            {
                "name": "sample-app",
                "url": "https://store.example/apps/sample-app.zip",
                "confirm": True,
            },
            {"name": ["sample-app"], "url": ["https://store.example/apps/sample-app.zip"]},
            "updatedApp",
        ),
        (
            "dns_set_app_config",
            "/api/apps/config/set",
            {"name": "sample-app", "config": '{"enabled":true}', "confirm": True},
            {"config": ['{"enabled":true}'], "name": ["sample-app"]},
            "ok",
        ),
        (
            "dns_uninstall_app",
            "/api/apps/uninstall",
            {"name": "sample-app", "confirm": True},
            {"name": ["sample-app"]},
            "ok",
        ),
    ],
)
async def test_app_mutation_tools_post_expected_payloads(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
    *,
    tool_name: str,
    endpoint: str,
    payload: dict[str, object],
    expected_params: dict[str, list[str]],
    response_key: str,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")
    httpx_mock.add_response(
        url=f"http://dns.local:5380{endpoint}",
        json={
            "status": "ok",
            "response": (
                {response_key: {"name": "sample-app"}}
                if response_key != "ok"
                else {"ok": True}
            ),
        },
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(tool_name, payload)

    if response_key == "ok":
        assert result.data == {"ok": True}
    else:
        assert result.data == {response_key: {"name": "sample-app"}}

    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {"token": ["token-123"], **expected_params}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "endpoint", "response_key"),
    [
        ("dns_install_app", "/api/apps/install", "installedApp"),
        ("dns_update_app", "/api/apps/update", "updatedApp"),
    ],
)
async def test_app_archive_upload_tools_send_multipart_form_data(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
    *,
    tool_name: str,
    endpoint: str,
    response_key: str,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")
    httpx_mock.add_response(
        url=f"http://dns.local:5380{endpoint}",
        json={"status": "ok", "response": {response_key: {"name": "sample-app"}}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            tool_name,
            {
                "name": "sample-app",
                "archive_base64": base64.b64encode(b"zip-data").decode(),
                "filename": "sample-app.zip",
                "confirm": True,
            },
        )

    assert result.data == {response_key: {"name": "sample-app"}}
    request = httpx_mock.get_request()
    assert request is not None
    assert "multipart/form-data" in request.headers["content-type"]
    assert b'name="token"' in request.content
    assert b'token-123' in request.content
    assert b'name="name"' in request.content
    assert b'sample-app' in request.content
    assert b'filename="sample-app.zip"' in request.content
    assert b'zip-data' in request.content
