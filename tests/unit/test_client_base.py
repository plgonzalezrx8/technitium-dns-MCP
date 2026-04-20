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
