# misraj.ai Python SDK

The official Python client for interacting with the misraj.ai API.

## Installation

```bash
pip install misraj.ai
```

## Setup

Set your API key as an environment variable (recommended):

```bash
export MISRAJ_API_KEY="your-api-key"
```

## Architecture Usage

The `misraj.ai` SDK is designed with decoupled services. You create a core HTTP `Client` first, and pass it to whatever specific service you need. This keeps the library robust and easy to extend.

### 1. Synchronous Usage

```python
from misraj import Client
from misraj.services import EmbeddingsService, OCRService

# The client automatically picks up the MISRAJ_API_KEY environment variable.
client = Client()

# Initialize our decoupled services using the core client transport
embeddings_service = EmbeddingsService(client)
ocr_service = OCRService(client)

# Text Embeddings
response = embeddings_service.create(input="Hello, misraj.ai!")
print(response.data[0].embedding)

# Batch Embeddings
batch_response = embeddings_service.batch_create(inputs=[
    "This is the first sentence.",
    "This is the second sentence."
])
print(batch_response.data)

# Basser OCR: Single Image Extraction
ocr_res = ocr_service.extract(image="document.jpg")
print(ocr_res.result.text)

# Basser OCR: Batch Image Extraction
batch_ocr_res = ocr_service.batch_extract(images=[
    "document1.png",
    b"raw_bytes...",
    "document2.jpg"
])
for res in batch_ocr_res.results:
    print(res.text)
```

### 2. Asynchronous Usage

For high-performance applications, use the `AsyncClient` and async services.

```python
import asyncio
from misraj import AsyncClient
from misraj.services import AsyncEmbeddingsService, AsyncOCRService

async def main():
    # You can also pass credentials explicitly if bypassing env variables
    async with AsyncClient(api_key="your-api-key") as client:
        
        # Initialize Async services
        embed_service = AsyncEmbeddingsService(client)
        ocr_service = AsyncOCRService(client)

        batch_embed_res = await embed_service.batch_create(
            inputs=["Concurrency is fast!", "Async batching is optimal."]
        )
        print(batch_embed_res)

        # Basser OCR Async Batch Extration
        batch_ocr_res = await ocr_service.batch_extract(
            images=["receipt_amount.png", "invoice.pdf"]
        )
        for r in batch_ocr_res.results:
            print(r.text)

if __name__ == "__main__":
    asyncio.run(main())
```

## Error Handling

```python
from misraj import Client
from misraj import MisrajAPIError, AuthenticationError, RateLimitError
from misraj.services import OCRService

try:
    client = Client()
    ocr = OCRService(client)
    ocr.extract("broken_file.jpg")
except AuthenticationError as e:
    print("Invalid API Key!", e)
except RateLimitError as e:
    print("Too many requests, slow down!", e)
except MisrajAPIError as e:
    print(f"Server error: {e.status_code}")
```

