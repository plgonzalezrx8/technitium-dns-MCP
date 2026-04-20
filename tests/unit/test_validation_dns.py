import pytest


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("example.com", "example.com"),
        ("_acme-challenge.example.com", "_acme-challenge.example.com"),
        ("_sip._tcp.example.com", "_sip._tcp.example.com"),
    ],
)
def test_validate_dns_name_accepts_real_world_dns_labels(name: str, expected: str) -> None:
    from technitium_dns_mcp.validation.dns import validate_dns_name

    assert validate_dns_name(name) == expected


def test_validate_dns_name_rejects_invalid_input() -> None:
    from technitium_dns_mcp.validation.dns import validate_dns_name

    with pytest.raises(ValueError):
        validate_dns_name("not valid domain")
