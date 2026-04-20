from __future__ import annotations

import re

LABEL_RE = re.compile(r"^[A-Za-z0-9_](?:[A-Za-z0-9_-]{0,61}[A-Za-z0-9_])?$")


def validate_dns_name(value: str) -> str:
    name = value.strip().lower()
    if not name:
        raise ValueError("DNS name is required")
    labels = name.split('.')
    if any(not label or not LABEL_RE.match(label) for label in labels):
        raise ValueError("Invalid DNS name")
    return name


def validate_zone_name(value: str) -> str:
    zone = validate_dns_name(value)
    if len(zone) > 253:
        raise ValueError("Invalid zone name")
    return zone
