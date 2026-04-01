import pathlib
from typing import List, Union, Tuple, Any
import asyncio
import aiofiles


from .base import BaseService, AsyncBaseService
from ..types import OCRResponse, BatchOCRResponse
from ..utils.pdf import convert_pdf_to_images
from ..utils.logging import get_logger

logger = get_logger(__name__)


FileTypes = Union[
    str,
    pathlib.Path,
    bytes,
    Tuple[str, Union[bytes, Any]],
    Tuple[str, Union[bytes, Any], str]
]


def _is_pdf(file_input: FileTypes) -> bool:
    """Helper to detect if a file input is a PDF by extension or magic bytes."""
    if isinstance(file_input, (str, pathlib.Path)):
        return str(file_input).lower().endswith(".pdf")
    elif isinstance(file_input, bytes):
        return file_input.startswith(b"%PDF-")
    elif isinstance(file_input, tuple):
        if isinstance(file_input[0], str) and file_input[0].lower().endswith(".pdf"):
            return True
        if isinstance(file_input[1], bytes) and file_input[1].startswith(b"%PDF-"):
            return True
    return False


async def _async_flatten_images(images: List[FileTypes]) -> List[FileTypes]:
    """Asynchronously flattens a list of inputs, expanding PDFs into multiple JPEGs."""
    flattened = []
    for img in images:
        if _is_pdf(img):
            # 1. Non-blocking File I/O
            if isinstance(img, (str, pathlib.Path)):
                async with aiofiles.open(img, mode='rb') as f:
                    pdf_bytes = await f.read()
            elif isinstance(img, tuple):
                pdf_bytes = img[1]
            else:
                pdf_bytes = img

            # 2. Non-blocking CPU Work (Offload to a thread)
            # This assumes convert_pdf_to_images is a synchronous, CPU-heavy function
            page_images = await asyncio.to_thread(convert_pdf_to_images, pdf_bytes)

            flattened.extend(page_images)
        else:
            flattened.append(img)
    return flattened


def _flatten_images(images: List[FileTypes]) -> List[FileTypes]:
    """Flattens a list of inputs, expanding PDFs into multiple individual JPEG pages."""
    flattened = []
    for img in images:
        if _is_pdf(img):
            if isinstance(img, (str, pathlib.Path)):
                pdf_bytes = pathlib.Path(img).read_bytes()
            elif isinstance(img, tuple):
                pdf_bytes = img[1]
            else:
                pdf_bytes = img

            page_images = convert_pdf_to_images(pdf_bytes)
            flattened.extend(page_images)
        else:
            flattened.append(img)
    return flattened


def _prepare_file(file_input: FileTypes) -> Tuple[str, Any, str]:
    """Helper to unify file inputs into a format httpx accepts."""
    if isinstance(file_input, (str, pathlib.Path)):
        path = pathlib.Path(file_input)
        return (path.name, path.read_bytes(), "application/octet-stream")
    elif isinstance(file_input, bytes):
        return ("image.jpeg", file_input, "application/octet-stream")
    elif isinstance(file_input, tuple):
        if len(file_input) == 2:
            return (file_input[0], file_input[1], "application/octet-stream")
        elif len(file_input) == 3:
            return file_input
    raise ValueError(f"Unsupported file input type: {type(file_input)}")


class OCRService(BaseService):
    """Synchronous Basser OCR service."""

    def extract(self,
                image: Union[FileTypes, List[FileTypes]],
                model: str = "misraj-basser") -> Union[OCRResponse]:
        """
        Extract text from a single image, a list of images, or multi-page PDFs using the Basser model.
        Returns an OCRResponse for a single non-PDF image or single-page PDF,
        and a BatchOCRResponse for a list of images or a multi-page PDF.
        """

        images_to_process = image if isinstance(image, list) else [image]
        flattened = _flatten_images(images_to_process)

        if not flattened:
            raise ValueError("No valid images or PDF pages found.")

        # Batch image path
        files = []
        for img in flattened:
            files.append(("images", _prepare_file(img)))

        data = {"model": model}
        response_data = self._client.request(
            "POST",
            "/ocr/extract",
            data=data,
            files=files
        )
        return OCRResponse(**response_data)


class AsyncOCRService(AsyncBaseService):
    """Asynchronous Basser OCR service."""

    async def extract(self,
                      image: Union[FileTypes, List[FileTypes]],
                      model: str = "misraj-basser") -> Union[OCRResponse]:
        """
        Extract text from a single image, a list of images, or multi-page PDFs asynchronously using the Basser model.
        Returns an OCRResponse for a single non-PDF image or single-page PDF,
        and a BatchOCRResponse for a list of images or a multi-page PDF.
        """
        images_to_process = image if isinstance(image, list) else [image]
        flattened = await _async_flatten_images(images_to_process)

        if not flattened:
            raise ValueError("No valid images or PDF pages found.")

        # Batch image path
        files = []
        for img in flattened:
            files.append(("images", _prepare_file(img)))

        data = {"model": model}
        response_data = await self._client.request(
            "POST",
            "/ocr/extract",
            data=data,
            files=files
        )
        return OCRResponse(**response_data)
