from urllib.parse import parse_qs

import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
async def test_dns_list_logs_calls_expected_endpoint(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/logs/list",
        json={
            "status": "ok",
            "response": {"logFiles": [{"fileName": "2026-04-20", "size": "4.2 KB"}]},
        },
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool("dns_list_logs", {"node": "secondary-1.example.net"})

    assert result.data == {"logFiles": [{"fileName": "2026-04-20", "size": "4.2 KB"}]}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "node": ["secondary-1.example.net"],
        "token": ["token-123"],
    }


@pytest.mark.asyncio
async def test_dns_download_log_returns_plaintext_content(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/logs/download",
        content=b"[INFO] started\n[WARN] throttled\n",
        headers={
            "content-type": "text/plain",
            "content-disposition": "attachment;filename=2026-04-20.log",
        },
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_download_log",
            {
                "file_name": "2026-04-20",
                "limit_mb": 2,
                "node": "secondary-1.example.net",
            },
        )

    assert result.data == {
        "content": "[INFO] started\n[WARN] throttled\n",
        "content_type": "text/plain",
        "filename": "2026-04-20.log",
    }
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "fileName": ["2026-04-20"],
        "limit": ["2"],
        "node": ["secondary-1.example.net"],
        "token": ["token-123"],
    }


@pytest.mark.asyncio
async def test_dns_query_logs_passes_filter_params(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/logs/query",
        json={
            "status": "ok",
            "response": {
                "pageNumber": 1,
                "totalPages": 1,
                "totalEntries": 1,
                "entries": [{"rowNumber": 1, "qname": "example.com", "qtype": "A"}],
            },
        },
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_query_logs",
            {
                "app_name": "QueryLogs",
                "class_path": "Technitium.Dns.Server.App.QueryLogs",
                "page_number": 1,
                "entries_per_page": 50,
                "descending_order": True,
                "start": "2026-04-20T00:00:00Z",
                "end": "2026-04-20T23:59:59Z",
                "client_ip_address": "192.168.1.10",
                "protocol": "Udp",
                "response_type": "Recursive",
                "rcode": "NoError",
                "qname": "example.com",
                "qtype": "A",
                "qclass": "IN",
                "node": "secondary-1.example.net",
            },
        )

    assert result.data == {
        "pageNumber": 1,
        "totalPages": 1,
        "totalEntries": 1,
        "entries": [{"rowNumber": 1, "qname": "example.com", "qtype": "A"}],
    }
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "name": ["QueryLogs"],
        "classPath": ["Technitium.Dns.Server.App.QueryLogs"],
        "pageNumber": ["1"],
        "entriesPerPage": ["50"],
        "descendingOrder": ["true"],
        "start": ["2026-04-20T00:00:00Z"],
        "end": ["2026-04-20T23:59:59Z"],
        "clientIpAddress": ["192.168.1.10"],
        "protocol": ["Udp"],
        "responseType": ["Recursive"],
        "rcode": ["NoError"],
        "qname": ["example.com"],
        "qtype": ["A"],
        "qclass": ["IN"],
        "node": ["secondary-1.example.net"],
        "token": ["token-123"],
    }


@pytest.mark.asyncio
async def test_dns_export_query_logs_returns_csv_content(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/logs/export",
        content=b"timestamp,qname,qtype\n2026-04-20T12:00:00Z,example.com,A\n",
        headers={
            "content-type": "text/csv",
            "content-disposition": "attachment;filename=query-logs.csv",
        },
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_export_query_logs",
            {
                "app_name": "QueryLogs",
                "class_path": "Technitium.Dns.Server.App.QueryLogs",
                "qname": "example.com",
            },
        )

    assert result.data == {
        "content": "timestamp,qname,qtype\n2026-04-20T12:00:00Z,example.com,A\n",
        "content_type": "text/csv",
        "filename": "query-logs.csv",
    }
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "name": ["QueryLogs"],
        "classPath": ["Technitium.Dns.Server.App.QueryLogs"],
        "qname": ["example.com"],
        "token": ["token-123"],
    }


@pytest.mark.asyncio
async def test_dns_delete_log_requires_destructive_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match="destructive"):
            await client.call_tool(
                "dns_delete_log",
                {"file_name": "2026-04-20", "confirm": False},
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "endpoint", "payload", "expected_params"),
    [
        (
            "dns_delete_log",
            "/api/logs/delete",
            {"file_name": "2026-04-20", "node": "secondary-1.example.net", "confirm": True},
            {"log": ["2026-04-20"], "node": ["secondary-1.example.net"]},
        ),
        (
            "dns_delete_all_logs",
            "/api/logs/deleteAll",
            {"node": "secondary-1.example.net", "confirm": True},
            {"node": ["secondary-1.example.net"]},
        ),
    ],
)
async def test_log_deletion_tools_call_expected_endpoints(
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
    assert parse_qs(request.content.decode()) == {"token": ["token-123"], **expected_params}
