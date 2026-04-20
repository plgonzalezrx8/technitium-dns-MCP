from __future__ import annotations

from fastmcp import FastMCP
from starlette.responses import JSONResponse

SERVICE_NAME = "technitium-dns-mcp"


def build_mcp_server() -> FastMCP:
    mcp = FastMCP(SERVICE_NAME)

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request):  # type: ignore[no-untyped-def]
        return JSONResponse({"status": "ok", "service": SERVICE_NAME})

    return mcp


def create_http_app():  # type: ignore[no-untyped-def]
    return build_mcp_server().http_app(path="/mcp")
