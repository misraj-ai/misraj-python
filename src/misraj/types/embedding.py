from pydantic import BaseModel, Field
from typing import List, Union, Optional, Literal


class EmbeddingUsage(BaseModel):
    promptTokens: int
    totalTokens: int


class EmbeddingData(BaseModel):
    object: str = "embedding"
    index: int
    embedding: List[float]


class EmbeddingResponse(BaseModel):
    data: Union[EmbeddingData, List[EmbeddingData]]
    model: str
    usage: EmbeddingUsage


class EmbeddingRequest(BaseModel):
    model: str
    input: Union[str, List[str]]
    dimensions: Optional[int] = None
    normalize: Optional[bool] = None
    promptName: Optional[str] = None
    truncate: Optional[bool] = None
    truncationDirection: Optional[Literal["Left", "Right"]] = None
