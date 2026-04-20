from __future__ import annotations

from typing import Any, cast

import httpx

from technitium_dns_mcp.client.errors import InvalidTokenError, TechnitiumApiError
from technitium_dns_mcp.client.models import RequestParams
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

    async def request(
        self, path: str, params: RequestParams | None = None
    ) -> dict[str, Any]:
        payload = {"token": self.token, **serialize_params(params)}
        async with httpx.AsyncClient(timeout=self.timeout, verify=self.verify) as client:
            response = await client.post(f"{self.base_url}{path}", data=payload)
            data = cast(dict[str, Any], response.json())

        status = data.get("status")
        if status == "ok":
            return cast(dict[str, Any], data.get("response", {}))
        if status == "invalid-token":
            raise InvalidTokenError(data.get("errorMessage", "Invalid token"))
        raise TechnitiumApiError(data.get("errorMessage", f"Technitium API error: {status}"))

    async def call_or_throw(
        self, endpoint: str, params: RequestParams | None = None
    ) -> dict[str, Any]:
        return await self.request(endpoint, params)
