from __future__ import annotations

from typing import Any, cast

import httpx

from technitium_dns_mcp.client.errors import InvalidTokenError, TechnitiumApiError
from technitium_dns_mcp.client.models import (
    DownloadResponse,
    RequestHeaders,
    RequestParams,
    UploadFiles,
)
from technitium_dns_mcp.validation.common import serialize_params


class TechnitiumClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: float = 10.0,
        verify: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.verify = verify

    async def _post(
        self,
        path: str,
        params: RequestParams | None = None,
        *,
        files: UploadFiles | None = None,
        headers: RequestHeaders | None = None,
    ) -> httpx.Response:
        payload = {"token": self.token, **serialize_params(params)}
        async with httpx.AsyncClient(timeout=self.timeout, verify=self.verify) as client:
            if files is None:
                return await client.post(f"{self.base_url}{path}", data=payload, headers=headers)
            return await client.post(
                f"{self.base_url}{path}",
                data=payload,
                files=files,
                headers=headers,
            )

    def _parse_json_payload(self, data: dict[str, Any]) -> dict[str, Any]:
        status = data.get("status")
        if status == "ok":
            return cast(dict[str, Any], data.get("response", {}))
        if status == "invalid-token":
            raise InvalidTokenError(data.get("errorMessage", "Invalid token"))
        raise TechnitiumApiError(data.get("errorMessage", f"Technitium API error: {status}"))

    @staticmethod
    def _normalize_content_type(content_type: str | None) -> str | None:
        if content_type is None:
            return None
        return content_type.split(";", 1)[0].strip()

    @staticmethod
    def _extract_filename(content_disposition: str | None) -> str | None:
        if not content_disposition:
            return None
        for part in content_disposition.split(";"):
            candidate = part.strip()
            if candidate.lower().startswith("filename="):
                return candidate.split("=", 1)[1].strip('"') or None
        return None

    async def request(
        self,
        path: str,
        params: RequestParams | None = None,
        *,
        files: UploadFiles | None = None,
        headers: RequestHeaders | None = None,
    ) -> dict[str, Any]:
        response = await self._post(path, params, files=files, headers=headers)
        data = cast(dict[str, Any], response.json())
        return self._parse_json_payload(data)

    async def download(
        self,
        path: str,
        params: RequestParams | None = None,
        *,
        headers: RequestHeaders | None = None,
    ) -> DownloadResponse:
        response = await self._post(path, params, headers=headers)
        try:
            data = cast(dict[str, Any], response.json())
        except Exception:
            data = None

        if data is not None and "status" in data:
            self._parse_json_payload(data)
            raise TechnitiumApiError("Expected download content but received JSON payload.")

        return DownloadResponse(
            content=response.content,
            content_type=self._normalize_content_type(response.headers.get("content-type")),
            filename=self._extract_filename(response.headers.get("content-disposition")),
        )

    async def call_or_throw(
        self,
        endpoint: str,
        params: RequestParams | None = None,
        *,
        files: UploadFiles | None = None,
        headers: RequestHeaders | None = None,
    ) -> dict[str, Any]:
        return await self.request(endpoint, params, files=files, headers=headers)
