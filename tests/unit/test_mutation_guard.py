import pytest

from technitium_dns_mcp.guards import require_mutation_confirmation


def test_require_mutation_confirmation_rejects_unconfirmed_calls() -> None:
    with pytest.raises(PermissionError, match="confirm"):
        require_mutation_confirmation(confirm=False)


def test_require_mutation_confirmation_allows_confirmed_calls() -> None:
    require_mutation_confirmation(confirm=True)
