from __future__ import annotations


def require_mutation_confirmation(*, confirm: bool) -> None:
    if not confirm:
        raise PermissionError(
            "Mutation blocked. Re-run with confirm=True if you actually mean it."
        )


def require_destructive_confirmation(*, confirm: bool) -> None:
    if not confirm:
        raise PermissionError(
            "destructive action blocked. Re-run with confirm=True if you actually mean to "
            "delete, flush, reset, or restore state."
        )


def require_critical_admin_confirmation(
    *,
    confirm: bool,
    acknowledge: str | None,
    expected_acknowledgement: str,
) -> None:
    if not confirm:
        raise PermissionError(
            "Critical admin action blocked. Re-run with confirm=True and "
            f"acknowledge=\"{expected_acknowledgement}\" if you actually mean it."
        )
    if acknowledge != expected_acknowledgement:
        raise PermissionError(
            "Critical admin action blocked. Re-run with confirm=True and "
            f"acknowledge=\"{expected_acknowledgement}\" if you actually mean it."
        )
