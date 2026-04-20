from pathlib import Path


def test_docker_compose_declares_healthcheck() -> None:
    compose_file = Path("docker-compose.yml")

    assert compose_file.exists()
    content = compose_file.read_text(encoding="utf-8")
    assert "healthcheck:" in content
    assert "/health" in content
