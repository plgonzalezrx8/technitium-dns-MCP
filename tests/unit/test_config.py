from pathlib import Path

import pytest


def test_load_settings_reads_token_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://192.168.1.248:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "secret-token")
    monkeypatch.setenv("TECHNITIUM_READONLY", "true")
    monkeypatch.setenv("MCP_HOST", "127.0.0.1")
    monkeypatch.setenv("MCP_PORT", "9000")

    from technitium_dns_mcp.config import load_settings

    settings = load_settings()

    assert settings.technitium_url == "http://192.168.1.248:5380"
    assert settings.technitium_token == "secret-token"
    assert settings.technitium_readonly is True
    assert settings.mcp_host == "127.0.0.1"
    assert settings.mcp_port == 9000


def test_load_settings_reads_token_from_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    token_file = tmp_path / "token.txt"
    token_file.write_text("file-token\n", encoding="utf-8")

    monkeypatch.setenv("TECHNITIUM_URL", "http://192.168.1.248:5380")
    monkeypatch.delenv("TECHNITIUM_TOKEN", raising=False)
    monkeypatch.setenv("TECHNITIUM_TOKEN_FILE", str(token_file))

    from technitium_dns_mcp.config import load_settings

    settings = load_settings()

    assert settings.technitium_token == "file-token"


def test_load_settings_requires_url_and_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TECHNITIUM_URL", raising=False)
    monkeypatch.delenv("TECHNITIUM_TOKEN", raising=False)
    monkeypatch.delenv("TECHNITIUM_TOKEN_FILE", raising=False)

    from technitium_dns_mcp.config import load_settings

    with pytest.raises(ValueError):
        load_settings()
