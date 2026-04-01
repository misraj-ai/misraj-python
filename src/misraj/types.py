from typing import List, Optional, Union
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Embeddings Models
# ---------------------------------------------------------


class EmbeddingRequest(BaseModel):
    """Payload for creating text embeddings."""
    input: Union[str, List[str]] = Field(
        ..., description="The string or list of strings to embed."
    )
    model: str = Field(..., description="The model to use for embedding.")
    dimensions: Optional[int] = Field(None, description="Optional dimensions to output.")


class EmbeddingData(BaseModel):
    """Holds a single embedding vector and its index within a batch."""
    embedding: List[float]
    index: int
    object: str = "embedding"


class EmbeddingResponse(BaseModel):
    """Response returned from the embeddings endpoint."""
    data: List[EmbeddingData]
    model: str
    usage: Optional[dict] = None
    object: str = "list"


# ---------------------------------------------------------
# OCR (Basser) Models
# ---------------------------------------------------------

class OCRResult(BaseModel):
    """The result of extracting text from a single image."""
    text: str
    confidence: Optional[float] = None


class OCRResponse(BaseModel):
    """Standard response from the Basser OCR endpoint for a single image."""
    result: OCRResult
    model: str


class BatchOCRResponse(BaseModel):
    """Response from the Basser OCR endpoint for a batch of images."""
    results: List[OCRResult]
    model: str
    batch_size: int
