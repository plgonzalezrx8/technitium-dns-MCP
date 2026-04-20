import pytest
from pytest_httpx import HTTPXMock


@pytest.mark.asyncio
async def test_call_or_throw_posts_form_encoded_token(httpx_mock: HTTPXMock) -> None:
    from technitium_dns_mcp.client.base import TechnitiumClient

    httpx_mock.add_response(
        url="http://192.168.1.248:5380/api/settings/get",
        json={"status": "ok", "response": {"version": "14.3"}},
    )

    client = TechnitiumClient(base_url="http://192.168.1.248:5380", token="token-123")
    result = await client.call_or_throw("/api/settings/get")

    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "POST"
    assert request.content == b"token=token-123"
    assert result == {"version": "14.3"}


@pytest.mark.asyncio
async def test_call_or_throw_raises_invalid_token_error(httpx_mock: HTTPXMock) -> None:
    from technitium_dns_mcp.client.base import TechnitiumClient
    from technitium_dns_mcp.client.errors import InvalidTokenError

    httpx_mock.add_response(
        url="http://192.168.1.248:5380/api/settings/get",
        json={"status": "invalid-token", "errorMessage": "expired"},
    )

    client = TechnitiumClient(base_url="http://192.168.1.248:5380", token="token-123")

    with pytest.raises(InvalidTokenError):
        await client.call_or_throw("/api/settings/get")


@pytest.mark.asyncio
async def test_call_or_throw_can_disable_ssl_verification(monkeypatch: pytest.MonkeyPatch) -> None:
    from technitium_dns_mcp.client.base import TechnitiumClient

    captured: dict[str, object] = {}

    class FakeResponse:
        def json(self) -> dict[str, object]:
            return {"status": "ok", "response": {"version": "14.3"}}

    class FakeAsyncClient:
        def __init__(self, *, timeout: float, verify: bool) -> None:
            captured["timeout"] = timeout
            captured["verify"] = verify

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
            return None

        async def post(self, url: str, data: dict[str, str]) -> FakeResponse:
            captured["url"] = url
            captured["data"] = data
            return FakeResponse()

    monkeypatch.setattr("technitium_dns_mcp.client.base.httpx.AsyncClient", FakeAsyncClient)

    client = TechnitiumClient(
        base_url="https://technitium.web.lan",
        token="token-123",
        verify=False,
    )
    result = await client.call_or_throw("/api/settings/get")

    assert captured == {
        "timeout": 10.0,
        "verify": False,
        "url": "https://technitium.web.lan/api/settings/get",
        "data": {"token": "token-123"},
    }
    assert result == {"version": "14.3"}
