from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class OCRUploadResponse(BaseModel):
    fileId: str


class OCRStatusResponse(BaseModel):
    fileId: str
    status: Literal["pending", "processing", "completed", "failed"]


class OCRPage(BaseModel):
    index: int
    content: str


class OCRResult(BaseModel):
    fileId: str
    model: str
    pages: List[OCRPage]
    creditsConsumed: int


class OCRBatchResult(BaseModel):
    successful_results: List[OCRResult] = Field(default_factory=list)
    failed_files: List[str] = Field(default_factory=list)
