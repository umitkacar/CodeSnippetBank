"""Multipart Form Data Handling"""
from fastapi import FastAPI, File, UploadFile, Form
from typing import List, Optional

app = FastAPI()

@app.post("/upload-with-metadata/")
async def upload_with_metadata(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: List[str] = Form(default=[])
):
    """Upload file with metadata"""
    return {
        "filename": file.filename,
        "title": title,
        "description": description,
        "tags": tags,
        "content_type": file.content_type
    }

@app.post("/multi-file-upload/")
async def multi_file_upload(
    files: List[UploadFile] = File(...),
    category: str = Form(...),
    public: bool = Form(False)
):
    """Upload multiple files with form data"""
    return {
        "files": [{"filename": f.filename} for f in files],
        "category": category,
        "public": public,
        "count": len(files)
    }
