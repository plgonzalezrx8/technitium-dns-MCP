def test_sanitize_response_redacts_sensitive_keys() -> None:
    from technitium_dns_mcp.sanitize import sanitize_response

    sanitized = sanitize_response(
        {
            "token": "super-secret-token",
            "nested": {"password": "really-bad"},
            "safe": "value",
        }
    )

    assert sanitized == {
        "token": "[REDACTED]",
        "nested": {"password": "[REDACTED]"},
        "safe": "value",
    }


def test_sanitize_error_redacts_tokens_and_paths() -> None:
    from technitium_dns_mcp.sanitize import sanitize_error

    error = "token abcdef1234567890 leaked at /etc/secrets/token.txt"

    sanitized = sanitize_error(error)

    assert "abcdef1234567890" not in sanitized
    assert "/etc/secrets/token.txt" not in sanitized
