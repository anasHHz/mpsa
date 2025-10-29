"""
FastAPI Server Runner
Starts the REST API server for MPSA
"""
import logging
import uvicorn
from src.api.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Starting MPSA FastAPI server...")
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )