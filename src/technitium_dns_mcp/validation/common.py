from __future__ import annotations

from ipaddress import ip_address

from technitium_dns_mcp.client.models import RequestParams


def normalize_name(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def normalize_bool(value: bool | str, *, field_name: str) -> bool:
    if isinstance(value, bool):
        return value

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{field_name} must be a boolean value")


def normalize_optional_int(
    value: int | str | None,
    *,
    field_name: str,
    minimum: int | None = None,
) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer")
    if isinstance(value, int):
        normalized = value
    else:
        raw_value = value.strip()
        if not raw_value:
            raise ValueError(f"{field_name} is required")
        try:
            normalized = int(raw_value)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be an integer") from exc

    if minimum is not None and normalized < minimum:
        raise ValueError(f"{field_name} must be >= {minimum}")
    return normalized


def normalize_ip_address(value: str, *, field_name: str = "ip") -> str:
    raw_value = normalize_name(value, field_name=field_name)
    try:
        return str(ip_address(raw_value))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid IP address") from exc


def normalize_ttl(value: int | str, *, field_name: str = "ttl") -> int:
    normalized = normalize_optional_int(value, field_name=field_name, minimum=0)
    if normalized is None:
        raise ValueError(f"{field_name} is required")
    return normalized


def serialize_params(params: RequestParams | None) -> dict[str, str]:
    if not params:
        return {}

    normalized: dict[str, str] = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            normalized[key] = "true" if value else "false"
            continue
        normalized[key] = str(value)
    return normalized
