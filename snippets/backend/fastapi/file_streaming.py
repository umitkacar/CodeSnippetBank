"""File Streaming"""
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import io

app = FastAPI()

async def generate_csv_data():
    """Generate CSV data in chunks"""
    yield "id,name,value\n"
    for i in range(1000):
        await asyncio.sleep(0.001)
        yield f"{i},Item {i},{i * 10}\n"

@app.get("/download-csv")
async def download_csv():
    """Stream CSV file download"""
    return StreamingResponse(
        generate_csv_data(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=data.csv"}
    )

async def generate_large_file():
    """Generate large file in chunks"""
    for i in range(10000):
        yield f"Line {i}\n".encode()

@app.get("/download-large")
async def download_large_file():
    """Stream large file"""
    return StreamingResponse(
        generate_large_file(),
        media_type="text/plain"
    )
