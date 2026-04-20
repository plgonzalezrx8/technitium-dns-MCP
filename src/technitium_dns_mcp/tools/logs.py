from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.client.endpoint_catalog import get_endpoint
from technitium_dns_mcp.client.models import DownloadResponse
from technitium_dns_mcp.guards import require_destructive_confirmation
from technitium_dns_mcp.validation import (
    normalize_ip_address,
    normalize_name,
    normalize_optional_int,
    normalize_optional_name,
)

LIST_LOGS_ENDPOINT = get_endpoint("dns_list_logs")
DOWNLOAD_LOG_ENDPOINT = get_endpoint("dns_download_log")
DELETE_LOG_ENDPOINT = get_endpoint("dns_delete_log")
DELETE_ALL_LOGS_ENDPOINT = get_endpoint("dns_delete_all_logs")
QUERY_LOGS_ENDPOINT = get_endpoint("dns_query_logs")
EXPORT_QUERY_LOGS_ENDPOINT = get_endpoint("dns_export_query_logs")


def _normalize_log_filters(
    *,
    app_name: str,
    class_path: str,
    start: str | None = None,
    end: str | None = None,
    client_ip_address: str | None = None,
    protocol: str | None = None,
    response_type: str | None = None,
    rcode: str | None = None,
    qname: str | None = None,
    qtype: str | None = None,
    qclass: str | None = None,
    node: str | None = None,
) -> dict[str, str | None]:
    return {
        "name": normalize_name(app_name, field_name="app_name"),
        "classPath": normalize_name(class_path, field_name="class_path"),
        "start": normalize_optional_name(start, field_name="start"),
        "end": normalize_optional_name(end, field_name="end"),
        "clientIpAddress": (
            normalize_ip_address(client_ip_address, field_name="client_ip_address")
            if client_ip_address is not None
            else None
        ),
        "protocol": normalize_optional_name(protocol, field_name="protocol"),
        "responseType": normalize_optional_name(response_type, field_name="response_type"),
        "rcode": normalize_optional_name(rcode, field_name="rcode"),
        "qname": normalize_optional_name(qname, field_name="qname"),
        "qtype": normalize_optional_name(qtype, field_name="qtype"),
        "qclass": normalize_optional_name(qclass, field_name="qclass"),
        "node": normalize_optional_name(node, field_name="node"),
    }


def _download_to_text_response(response: DownloadResponse) -> dict[str, str | None]:
    return {
        "content": response.content.decode("utf-8"),
        "content_type": response.content_type,
        "filename": response.filename,
    }


def register_log_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_list_logs(node: str | None = None) -> dict[str, Any]:
        return await client.call_or_throw(
            LIST_LOGS_ENDPOINT.api_path,
            {"node": normalize_optional_name(node, field_name="node")},
        )

    @mcp.tool
    async def dns_download_log(
        file_name: str,
        limit_mb: int | str | None = None,
        node: str | None = None,
    ) -> dict[str, str | None]:
        response = await client.download(
            DOWNLOAD_LOG_ENDPOINT.api_path,
            {
                "fileName": normalize_name(file_name, field_name="file_name"),
                "limit": normalize_optional_int(limit_mb, field_name="limit_mb", minimum=0),
                "node": normalize_optional_name(node, field_name="node"),
            },
        )
        return _download_to_text_response(response)

    @mcp.tool
    async def dns_query_logs(
        app_name: str,
        class_path: str,
        page_number: int | str | None = None,
        entries_per_page: int | str | None = None,
        descending_order: bool | None = None,
        start: str | None = None,
        end: str | None = None,
        client_ip_address: str | None = None,
        protocol: str | None = None,
        response_type: str | None = None,
        rcode: str | None = None,
        qname: str | None = None,
        qtype: str | None = None,
        qclass: str | None = None,
        node: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            **_normalize_log_filters(
                app_name=app_name,
                class_path=class_path,
                start=start,
                end=end,
                client_ip_address=client_ip_address,
                protocol=protocol,
                response_type=response_type,
                rcode=rcode,
                qname=qname,
                qtype=qtype,
                qclass=qclass,
                node=node,
            ),
            "pageNumber": normalize_optional_int(page_number, field_name="page_number", minimum=1),
            "entriesPerPage": normalize_optional_int(
                entries_per_page,
                field_name="entries_per_page",
                minimum=1,
            ),
            "descendingOrder": descending_order,
        }
        return await client.call_or_throw(QUERY_LOGS_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_export_query_logs(
        app_name: str,
        class_path: str,
        start: str | None = None,
        end: str | None = None,
        client_ip_address: str | None = None,
        protocol: str | None = None,
        response_type: str | None = None,
        rcode: str | None = None,
        qname: str | None = None,
        qtype: str | None = None,
        qclass: str | None = None,
        node: str | None = None,
    ) -> dict[str, str | None]:
        response = await client.download(
            EXPORT_QUERY_LOGS_ENDPOINT.api_path,
            _normalize_log_filters(
                app_name=app_name,
                class_path=class_path,
                start=start,
                end=end,
                client_ip_address=client_ip_address,
                protocol=protocol,
                response_type=response_type,
                rcode=rcode,
                qname=qname,
                qtype=qtype,
                qclass=qclass,
                node=node,
            ),
        )
        return _download_to_text_response(response)


def register_log_mutation_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_delete_log(
        file_name: str,
        node: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        return await client.call_or_throw(
            DELETE_LOG_ENDPOINT.api_path,
            {
                "log": normalize_name(file_name, field_name="file_name"),
                "node": normalize_optional_name(node, field_name="node"),
            },
        )

    @mcp.tool
    async def dns_delete_all_logs(
        node: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        return await client.call_or_throw(
            DELETE_ALL_LOGS_ENDPOINT.api_path,
            {"node": normalize_optional_name(node, field_name="node")},
        )
