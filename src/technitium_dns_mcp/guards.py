from __future__ import annotations


def require_mutation_confirmation(*, confirm: bool) -> None:
    if not confirm:
        raise PermissionError(
            "Mutation blocked. Re-run with confirm=True if you actually mean it."
        )
