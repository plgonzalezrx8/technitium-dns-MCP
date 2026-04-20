from starlette.testclient import TestClient


def test_health_endpoint_reports_service_status() -> None:
    from technitium_dns_mcp.app import create_http_app

    app = create_http_app()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "technitium-dns-mcp",
    }
