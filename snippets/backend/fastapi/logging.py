"""Logging Configuration"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import sys
from datetime import datetime
import json

app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

# Custom formatter for JSON logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# Endpoints with logging
@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Hello World"}

@app.get("/error")
async def trigger_error():
    logger.error("Error endpoint called")
    try:
        raise ValueError("This is a test error")
    except ValueError as e:
        logger.exception("An error occurred")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/debug")
async def debug_info():
    logger.debug("Debug information requested")
    return {"debug": "This is debug info"}
