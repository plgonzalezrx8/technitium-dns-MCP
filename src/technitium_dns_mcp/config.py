from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    technitium_url: str = Field(alias="TECHNITIUM_URL")
    technitium_token: str | None = Field(default=None, alias="TECHNITIUM_TOKEN")
    technitium_token_file: Path | None = Field(default=None, alias="TECHNITIUM_TOKEN_FILE")
    technitium_readonly: bool = Field(default=False, alias="TECHNITIUM_READONLY")
    technitium_verify_ssl: bool = Field(default=True, alias="TECHNITIUM_VERIFY_SSL")
    technitium_log_level: str = Field(default="INFO", alias="TECHNITIUM_LOG_LEVEL")
    mcp_host: str = Field(default="0.0.0.0", alias="MCP_HOST")
    mcp_port: int = Field(default=8000, alias="MCP_PORT")


def load_settings() -> Settings:
    try:
        settings = Settings()  # type: ignore[call-arg]
    except Exception as exc:  # pragma: no cover - pydantic error text is enough
        raise ValueError("TECHNITIUM_URL is required") from exc

    token = settings.technitium_token
    if token is None and settings.technitium_token_file is not None:
        token = settings.technitium_token_file.read_text(encoding="utf-8").strip()

    if not token:
        raise ValueError("TECHNITIUM_TOKEN or TECHNITIUM_TOKEN_FILE is required")

    settings.technitium_token = token
    return settings
