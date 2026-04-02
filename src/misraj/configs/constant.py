import os

# Base configurations
BASE_URL = os.getenv("MISRAJ_BASE_URL", "https://api-dev.kawn.ai/")
DEFAULT_TIMEOUT = 60.0
POLL_INTERVAL = 2.0  # Seconds to wait between status checks for async tasks
MAX_RETRIES = 3
OCR_MODEL = 'baseer/baseer-v2'
EMBEDDING_MODEL = 'tbyaan/islamic-embedding-tbyaan-v1'
# Batch constraints
MAX_OCR_BATCH_SIZE = 32
MAX_EMBEDDING_BATCH_SIZE = 64
MAX_THREAD_FOR_BATCH_REQUEST = 8

