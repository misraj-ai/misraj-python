import asyncio
import os
import time
import json
from pathlib import Path
from typing import Union, List, Optional
from concurrent.futures import ThreadPoolExecutor

from base import AsyncBaseService, BaseService
from src.misraj.types.ocr import OCRUploadResponse, OCRStatusResponse, OCRResult, OCRBatchResult
from src.misraj.configs.constant import POLL_INTERVAL, MAX_OCR_BATCH_SIZE, OCR_MODEL, MAX_THREAD_FOR_BATCH_REQUEST
from src.misraj.exceptions import ProcessingFailedError, InvalidRequestError
from src.misraj.utils.logging import get_logger

logger = get_logger("[OCR Service]")


class OCRService(BaseService):

    def get_result(self, file_id) -> OCRResult:
        result_res = self._client.request("GET", f"/ocr/{file_id}/results")
        return OCRResult(**result_res.json())

    def process_file(self,
                     file_path: Union[str, Path],
                     model: Optional[str] = None,
                     options: Optional[dict] = None,
                     return_result: Optional[bool] = True) -> Union[OCRResult, str]:

        file_path = Path(file_path)
        data = {"model": model if model else OCR_MODEL}

        if options:
            data["options"] = json.dumps(options)

        # 1. Upload
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            res = self._client.request("POST", "/ocr", data=data, files=files)

        file_id = OCRUploadResponse(**res.json()).fileId

        logger.info(f"OCR request has correctly upload "
                    f"the file to the server and receive task job id: {file_id}")

        logger.info("Waiting the response...")
        # 2. Poll
        while True:
            status_res = self._client.request("GET", f"/ocr/{file_id}/status")
            status_data = OCRStatusResponse(**status_res.json())
            if status_data.status == "completed":
                break
            elif status_data.status == "failed":
                raise ProcessingFailedError(f"OCR processing failed for file {file_id}")
            time.sleep(POLL_INTERVAL)

        logger.info("The processing done successfully, we will get the result.")
        if not return_result:
            logger.info("You decided not to receive the result immediately,"
                        "you will receive the Task id, and can access the result by "
                        "calling get_result(task_id)")
            return file_id

        logger.warning("Please save the result, as it will be deleted as long as you requested from the server.")
        # 3. Retrieve
        return self.get_result(file_id)

    def process_batch(self,
                      file_paths: List[Union[str, Path]],
                      model: Optional[str] = None,
                      options: Optional[dict] = None) -> OCRBatchResult:

        if len(file_paths) > MAX_OCR_BATCH_SIZE:
            raise InvalidRequestError(f"Batch size exceeds {MAX_OCR_BATCH_SIZE}")

        batch_result = OCRBatchResult()
        with ThreadPoolExecutor(max_workers=min(len(file_paths), MAX_THREAD_FOR_BATCH_REQUEST)) as executor:
            future_to_path = {executor.submit(self.process_file, fp, model, options): fp for fp in file_paths}
            for future in future_to_path:
                try:
                    batch_result.successful_results.append(future.result())
                except Exception as exc:
                    batch_result.failed_files.append(str(future_to_path[future]))
        return batch_result


class AsyncOCRService(AsyncBaseService):

    async def get_result(self, file_id) -> OCRResult:
        result_res = await self._client.request("GET", f"/ocr/{file_id}/results")
        return OCRResult(**result_res.json())

    async def process_file(self,
                           file_path: Union[str, Path],
                           model: Optional[str] = None,
                           options: Optional[dict] = None,
                           return_result: Optional[bool] = True) -> Union[OCRResult, str]:
        file_path = Path(file_path)
        data = {"model": model if model else OCR_MODEL}
        if options:
            data["options"] = json.dumps(options)

        with open(file_path, "rb") as f:
            file = {"file": (file_path.name, f)}
            res = await self._client.request("POST", "/ocr", data=data, files=file)

        file_id = OCRUploadResponse(**res.json()).fileId

        logger.info(f"OCR request has correctly upload "
                    f"the file to the server and receive task job id: {file_id}")

        logger.info("Waiting the response...")

        while True:
            status_res = await self._client.request("GET", f"/ocr/{file_id}/status")
            status_data = OCRStatusResponse(**status_res.json())
            if status_data.status == "completed":
                break
            elif status_data.status == "failed":
                raise ProcessingFailedError(f"OCR processing failed for file {file_id}")
            await asyncio.sleep(POLL_INTERVAL)

        logger.info("The processing done successfully, we will get the result.")
        if not return_result:
            logger.info("You decided not to receive the result immediately,"
                        "you will receive the Task id, and can access the result by "
                        "using await get_result(task_id)")
            return file_id

        logger.warning("Please save the result, as it will be deleted as long as you requested from the server.")
        return await self.get_result(file_id)

    async def process_batch(self,
                            file_paths: List[Union[str, Path]],
                            model: Optional[str] = None,
                            options: Optional[dict] = None) -> OCRBatchResult:

        if len(file_paths) > MAX_OCR_BATCH_SIZE:
            raise InvalidRequestError(f"Batch size exceeds {MAX_OCR_BATCH_SIZE}")

        tasks = [self.process_file(fp, model, options) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        batch_result = OCRBatchResult()
        for fp, result in zip(file_paths, results):
            if isinstance(result, Exception):
                batch_result.failed_files.append(str(fp))
            else:
                batch_result.successful_results.append(result)
        return batch_result

