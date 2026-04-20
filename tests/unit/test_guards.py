import pytest

from technitium_dns_mcp.guards import (
    require_critical_admin_confirmation,
    require_destructive_confirmation,
    require_mutation_confirmation,
)


def test_require_mutation_confirmation_rejects_unconfirmed_calls() -> None:
    with pytest.raises(PermissionError, match="confirm"):
        require_mutation_confirmation(confirm=False)


def test_require_mutation_confirmation_allows_confirmed_calls() -> None:
    require_mutation_confirmation(confirm=True)


def test_require_destructive_confirmation_rejects_unconfirmed_calls() -> None:
    with pytest.raises(PermissionError, match="destructive"):
        require_destructive_confirmation(confirm=False)


def test_require_destructive_confirmation_allows_confirmed_calls() -> None:
    require_destructive_confirmation(confirm=True)


@pytest.mark.parametrize(
    ("confirm", "acknowledge", "expected_message"),
    [
        (False, "cluster", "confirm=True"),
        (True, None, "acknowledge=\"cluster\""),
        (True, "delete-user", "acknowledge=\"cluster\""),
    ],
)
def test_require_critical_admin_confirmation_rejects_missing_confirmation_state(
    *, confirm: bool, acknowledge: str | None, expected_message: str
) -> None:
    with pytest.raises(PermissionError, match=expected_message):
        require_critical_admin_confirmation(
            confirm=confirm,
            acknowledge=acknowledge,
            expected_acknowledgement="cluster",
        )


def test_require_critical_admin_confirmation_allows_exact_acknowledgement() -> None:
    require_critical_admin_confirmation(
        confirm=True,
        acknowledge="cluster",
        expected_acknowledgement="cluster",
    )
