from src.misraj.client import MisrajClient, AsyncMisrajClient


class BaseService:
    """Base synchronous service."""

    def __init__(self, client: MisrajClient):
        if not isinstance(client, MisrajClient):
            raise TypeError("Expected a MisrajClient instance.")
        self._client = client


class AsyncBaseService:
    """Base asynchronous service."""

    def __init__(self, client: AsyncMisrajClient):
        if not isinstance(client, AsyncMisrajClient):
            raise TypeError("Expected a AsyncMisrajClient instance.")
        self._client = client
