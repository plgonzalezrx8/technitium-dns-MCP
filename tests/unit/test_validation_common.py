import pytest


def test_normalize_name_strips_and_rejects_blank_values() -> None:
    from technitium_dns_mcp.validation.common import normalize_name

    assert normalize_name("  Example Zone  ", field_name="zone") == "Example Zone"

    with pytest.raises(ValueError, match="zone"):
        normalize_name("   ", field_name="zone")


@pytest.mark.parametrize(
    ("value", "expected"),
    [(True, True), (False, False), ("true", True), (" FALSE ", False), ("1", True), ("0", False)],
)
def test_normalize_bool_accepts_common_boolean_inputs(value: bool | str, expected: bool) -> None:
    from technitium_dns_mcp.validation.common import normalize_bool

    assert normalize_bool(value, field_name="enabled") is expected


def test_normalize_optional_int_supports_none_and_bounds() -> None:
    from technitium_dns_mcp.validation.common import normalize_optional_int

    assert normalize_optional_int(None, field_name="limit", minimum=1) is None
    assert normalize_optional_int(" 42 ", field_name="limit", minimum=1) == 42

    with pytest.raises(ValueError, match="limit"):
        normalize_optional_int("0", field_name="limit", minimum=1)


def test_normalize_ip_address_returns_canonical_value() -> None:
    from technitium_dns_mcp.validation.common import normalize_ip_address

    assert normalize_ip_address("2001:0db8:0:0:0:0:0:1", field_name="server") == "2001:db8::1"

    with pytest.raises(ValueError, match="server"):
        normalize_ip_address("not-an-ip", field_name="server")


def test_normalize_ttl_requires_non_negative_integer() -> None:
    from technitium_dns_mcp.validation.common import normalize_ttl

    assert normalize_ttl("3600") == 3600

    with pytest.raises(ValueError, match="ttl"):
        normalize_ttl(-1)


def test_serialize_params_skips_none_and_stringifies_scalars() -> None:
    from technitium_dns_mcp.validation.common import serialize_params

    assert serialize_params(
        {
            "zone": "example.com",
            "limit": 100,
            "enabled": False,
            "comment": None,
        }
    ) == {
        "zone": "example.com",
        "limit": "100",
        "enabled": "false",
    }
