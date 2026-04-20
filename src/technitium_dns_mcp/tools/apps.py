from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.client.endpoint_catalog import get_endpoint
from technitium_dns_mcp.client.models import UploadFiles
from technitium_dns_mcp.guards import (
    require_destructive_confirmation,
    require_mutation_confirmation,
)
from technitium_dns_mcp.validation import normalize_name, resolve_upload_content

LIST_APPS_ENDPOINT = get_endpoint("dns_list_apps")
LIST_STORE_APPS_ENDPOINT = get_endpoint("dns_list_store_apps")
GET_APP_CONFIG_ENDPOINT = get_endpoint("dns_get_app_config")
DOWNLOAD_AND_INSTALL_APP_ENDPOINT = get_endpoint("dns_download_and_install_app")
DOWNLOAD_AND_UPDATE_APP_ENDPOINT = get_endpoint("dns_download_and_update_app")
INSTALL_APP_ENDPOINT = get_endpoint("dns_install_app")
UPDATE_APP_ENDPOINT = get_endpoint("dns_update_app")
UNINSTALL_APP_ENDPOINT = get_endpoint("dns_uninstall_app")
SET_APP_CONFIG_ENDPOINT = get_endpoint("dns_set_app_config")


def _normalize_https_url(value: str) -> str:
    normalized = normalize_name(value, field_name="url")
    parsed = urlparse(normalized)
    if parsed.scheme.lower() != "https" or not parsed.netloc:
        raise ValueError("url must be an https URL")
    return normalized


def _app_archive_files(
    *,
    archive_path: str | None,
    archive_base64: str | None,
    filename: str | None,
) -> UploadFiles:
    resolved_filename, content = resolve_upload_content(
        file_path=archive_path,
        content_base64=archive_base64,
        filename=filename,
        default_filename="app.zip",
        field_name="archive",
    )
    return {"file": (resolved_filename, content, "application/zip")}


def register_app_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_list_apps() -> dict[str, Any]:
        return await client.call_or_throw(LIST_APPS_ENDPOINT.api_path)

    @mcp.tool
    async def dns_list_store_apps() -> dict[str, Any]:
        return await client.call_or_throw(LIST_STORE_APPS_ENDPOINT.api_path)

    @mcp.tool
    async def dns_get_app_config(name: str) -> dict[str, Any]:
        return await client.call_or_throw(
            GET_APP_CONFIG_ENDPOINT.api_path,
            {"name": normalize_name(name, field_name="name")},
        )


def register_app_mutation_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_download_and_install_app(
        name: str,
        url: str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            DOWNLOAD_AND_INSTALL_APP_ENDPOINT.api_path,
            {
                "name": normalize_name(name, field_name="name"),
                "url": _normalize_https_url(url),
            },
        )

    @mcp.tool
    async def dns_download_and_update_app(
        name: str,
        url: str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            DOWNLOAD_AND_UPDATE_APP_ENDPOINT.api_path,
            {
                "name": normalize_name(name, field_name="name"),
                "url": _normalize_https_url(url),
            },
        )

    @mcp.tool
    async def dns_install_app(
        name: str,
        archive_path: str | None = None,
        archive_base64: str | None = None,
        filename: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            INSTALL_APP_ENDPOINT.api_path,
            {"name": normalize_name(name, field_name="name")},
            files=_app_archive_files(
                archive_path=archive_path,
                archive_base64=archive_base64,
                filename=filename,
            ),
        )

    @mcp.tool
    async def dns_update_app(
        name: str,
        archive_path: str | None = None,
        archive_base64: str | None = None,
        filename: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            UPDATE_APP_ENDPOINT.api_path,
            {"name": normalize_name(name, field_name="name")},
            files=_app_archive_files(
                archive_path=archive_path,
                archive_base64=archive_base64,
                filename=filename,
            ),
        )

    @mcp.tool
    async def dns_uninstall_app(name: str, confirm: bool = False) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        return await client.call_or_throw(
            UNINSTALL_APP_ENDPOINT.api_path,
            {"name": normalize_name(name, field_name="name")},
        )

    @mcp.tool
    async def dns_set_app_config(
        name: str,
        config: str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            SET_APP_CONFIG_ENDPOINT.api_path,
            {
                "name": normalize_name(name, field_name="name"),
                "config": config,
            },
        )
