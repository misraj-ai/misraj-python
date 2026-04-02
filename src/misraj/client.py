import httpx
from typing import Optional
from .exceptions import AuthenticationError, handle_http_error
from .configs.settings import get_api_key_from_environment
from .configs.constant import BASE_URL, DEFAULT_TIMEOUT


def _resolve_api_key(api_key: Optional[str]) -> str:
    key = api_key or get_api_key_from_environment()
    if not key:
        raise AuthenticationError("API Key must be provided or set in MISRAJ_API_KEY.")
    return key


def _build_headers(api_key: str) -> dict:
    return {
        "x-api-key": api_key,
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }


class MisrajClient:
    """Synchronous HTTP engine."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: Optional[float] = None):
        self.api_key = _resolve_api_key(api_key)
        self.http_client = httpx.Client(
            base_url=base_url if base_url else BASE_URL,
            headers=_build_headers(self.api_key),
            timeout=timeout if timeout else DEFAULT_TIMEOUT,
        )

    def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        res = self.http_client.request(method, endpoint, **kwargs)
        if res.status_code >= 400:
            handle_http_error(res)
        return res

    def close(self):
        self.http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncMisrajClient:
    """Asynchronous HTTP engine."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: Optional[float] = None):
        self.api_key = _resolve_api_key(api_key)
        self.http_client = httpx.AsyncClient(
            base_url=base_url if base_url else BASE_URL,
            headers=_build_headers(self.api_key),
            timeout=timeout if timeout else DEFAULT_TIMEOUT,
        )

    async def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        res = await self.http_client.request(method, endpoint, **kwargs)
        if res.status_code >= 400:
            handle_http_error(res)
        return res

    async def close(self):
        await self.http_client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
