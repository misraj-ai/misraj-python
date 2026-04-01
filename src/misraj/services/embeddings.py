from typing import List, Union, Optional
from .base import BaseService, AsyncBaseService
from ..types import EmbeddingRequest, EmbeddingResponse


class EmbeddingsService(BaseService):
    """Synchronous embeddings service."""

    def create(self,
               input: Union[str, List[str]],
               model: str = "misraj-embed",
               dimensions: Optional[int] = None) -> EmbeddingResponse:
        """
        Create embeddings for a given input string or list of strings.
        """
        req = EmbeddingRequest(input=input, model=model, dimensions=dimensions)
        response_data = self._client.request(
            "POST", 
            "/embeddings", 
            json=req.model_dump(exclude_none=True)
        )
        return EmbeddingResponse(**response_data)


class AsyncEmbeddingsService(AsyncBaseService):
    """Asynchronous embeddings service."""

    async def create(self,
                     input: Union[str, List[str]],
                     model: str = "misraj-embed",
                     dimensions: Optional[int] = None) -> EmbeddingResponse:
        """
        Create embeddings for a given input string or list of strings asynchronously.
        """
        req = EmbeddingRequest(input=input, model=model, dimensions=dimensions)
        response_data = await self._client.request(
            "POST", 
            "/embeddings", 
            json=req.model_dump(exclude_none=True)
        )
        return EmbeddingResponse(**response_data)
