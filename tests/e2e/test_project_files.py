from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_dockerfile_runs_as_non_root_with_healthcheck() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "USER app" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    assert "technitium_dns_mcp" in dockerfile


def test_compose_file_has_restart_policy_and_env_file() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "env_file:" in compose
    assert "restart: unless-stopped" in compose
    assert "healthcheck:" in compose


def test_ci_workflow_runs_quality_gates() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "uv sync --group dev" in workflow
    assert "uv run pytest -q" in workflow
    assert "uv run ruff check ." in workflow
    assert "uv run mypy src" in workflow


def test_readme_documents_safety_and_startup() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "TECHNITIUM_READONLY" in readme
    assert "confirm=True" in readme
    assert "docker compose up --build" in readme
