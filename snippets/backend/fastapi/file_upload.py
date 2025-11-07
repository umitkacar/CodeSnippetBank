"""File Upload Handling with FastAPI"""
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
import aiofiles
import os
from pathlib import Path
import shutil
from datetime import datetime
import mimetypes

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".txt", ".doc", ".docx"}

def validate_file(filename: str, file_size: int):
    """Validate file extension and size"""
    file_ext = Path(filename).suffix.lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed types: {ALLOWED_EXTENSIONS}"
        )

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes"
        )

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Upload a single file"""
    # Read file content to check size
    content = await file.read()
    file_size = len(content)

    validate_file(file.filename, file_size)

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = Path(file.filename).suffix
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename

    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)

    return {
        "filename": safe_filename,
        "size": file_size,
        "content_type": file.content_type,
        "path": str(file_path)
    }

@app.post("/upload-multiple/")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """Upload multiple files"""
    uploaded_files = []

    for file in files:
        content = await file.read()
        file_size = len(content)

        validate_file(file.filename, file_size)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = Path(file.filename).suffix
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)

        uploaded_files.append({
            "filename": safe_filename,
            "size": file_size,
            "content_type": file.content_type
        })

    return {"files": uploaded_files, "count": len(uploaded_files)}

@app.post("/upload-chunked/")
async def upload_chunked_file(file: UploadFile = File(...)):
    """Upload large file in chunks"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename

    chunk_size = 1024 * 1024  # 1MB chunks
    total_size = 0

    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await file.read(chunk_size):
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                await aiofiles.os.remove(file_path)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File size exceeds maximum allowed size"
                )
            await f.write(chunk)

    return {
        "filename": safe_filename,
        "size": total_size,
        "content_type": file.content_type
    }

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download a file"""
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

@app.get("/files/")
async def list_files():
    """List all uploaded files"""
    files = []
    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            files.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

    return {"files": files, "count": len(files)}

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a file"""
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_path.unlink()
    return {"message": f"File {filename} deleted successfully"}
