from __future__ import annotations

import base64
from typing import Any

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.client.endpoint_catalog import get_endpoint
from technitium_dns_mcp.client.models import UploadFiles
from technitium_dns_mcp.guards import (
    require_critical_admin_confirmation,
    require_mutation_confirmation,
)
from technitium_dns_mcp.validation import (
    normalize_optional_int,
    normalize_passthrough_params,
    resolve_upload_content,
)

GET_TSIG_KEY_NAMES_ENDPOINT = get_endpoint("dns_get_tsig_key_names")
SET_SETTINGS_ENDPOINT = get_endpoint("dns_set_settings")
FORCE_UPDATE_BLOCK_LISTS_ENDPOINT = get_endpoint("dns_force_update_block_lists")
TEMPORARY_DISABLE_BLOCKING_ENDPOINT = get_endpoint("dns_temporary_disable_blocking")
BACKUP_SETTINGS_ENDPOINT = get_endpoint("dns_backup_settings")
RESTORE_SETTINGS_ENDPOINT = get_endpoint("dns_restore_settings")


def _required_minutes(value: int | str) -> int:
    normalized = normalize_optional_int(value, field_name="minutes", minimum=1)
    if normalized is None:
        raise ValueError("minutes is required")
    return normalized


def _settings_archive_files(
    *,
    archive_path: str | None,
    archive_base64: str | None,
    filename: str | None,
) -> UploadFiles:
    resolved_filename, content = resolve_upload_content(
        file_path=archive_path,
        content_base64=archive_base64,
        filename=filename,
        default_filename="settings-backup.zip",
        field_name="archive",
    )
    return {"file": (resolved_filename, content, "application/zip")}


def register_settings_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_get_tsig_key_names() -> dict[str, Any]:
        return await client.call_or_throw(GET_TSIG_KEY_NAMES_ENDPOINT.api_path)


def register_settings_mutation_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_set_settings(
        options: dict[str, object] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            SET_SETTINGS_ENDPOINT.api_path,
            normalize_passthrough_params(options, field_name="options"),
        )

    @mcp.tool
    async def dns_force_update_block_lists(confirm: bool = False) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(FORCE_UPDATE_BLOCK_LISTS_ENDPOINT.api_path)

    @mcp.tool
    async def dns_temporary_disable_blocking(
        minutes: int | str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            TEMPORARY_DISABLE_BLOCKING_ENDPOINT.api_path,
            {"minutes": _required_minutes(minutes)},
        )

    @mcp.tool
    async def dns_backup_settings(
        options: dict[str, object] | None = None,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        require_critical_admin_confirmation(
            confirm=confirm,
            acknowledge=acknowledge,
            expected_acknowledgement="backup-settings",
        )
        response = await client.download(
            BACKUP_SETTINGS_ENDPOINT.api_path,
            normalize_passthrough_params(options, field_name="options"),
        )
        return {
            "content_base64": base64.b64encode(response.content).decode(),
            "content_type": response.content_type,
            "filename": response.filename,
            "size_bytes": len(response.content),
        }

    @mcp.tool
    async def dns_restore_settings(
        options: dict[str, object] | None = None,
        archive_path: str | None = None,
        archive_base64: str | None = None,
        filename: str | None = None,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        require_critical_admin_confirmation(
            confirm=confirm,
            acknowledge=acknowledge,
            expected_acknowledgement="restore-settings",
        )
        return await client.call_or_throw(
            RESTORE_SETTINGS_ENDPOINT.api_path,
            normalize_passthrough_params(options, field_name="options"),
            files=_settings_archive_files(
                archive_path=archive_path,
                archive_base64=archive_base64,
                filename=filename,
            ),
        )
