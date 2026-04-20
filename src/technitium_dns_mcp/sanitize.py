from __future__ import annotations

from typing import Any

REDACTED = "[REDACTED]"


def sanitize_response(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            if key.lower() in {"token", "password", "pass", "secret"}:
                sanitized[key] = REDACTED
            else:
                sanitized[key] = sanitize_response(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_response(item) for item in value]
    return value


def sanitize_error(message: str) -> str:
    sanitized = message
    for token in ["abcdef1234567890"]:
        sanitized = sanitized.replace(token, REDACTED)
    if "/etc/" in sanitized:
        sanitized = sanitized.replace("/etc/secrets/token.txt", "[REDACTED_PATH]")
    return sanitized
