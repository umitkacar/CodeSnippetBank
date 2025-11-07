"""Request and Response Handling"""
from fastapi import FastAPI, Request, Response, Cookie, Header, status
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse, StreamingResponse, RedirectResponse
from typing import Optional
import json
import io

app = FastAPI()

# Request information
@app.get("/request-info")
async def get_request_info(request: Request):
    """Get detailed request information"""
    return {
        "method": request.method,
        "url": str(request.url),
        "base_url": str(request.base_url),
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "path_params": dict(request.path_params),
        "client_host": request.client.host,
        "cookies": request.cookies
    }

# Custom headers
@app.get("/with-custom-headers")
async def with_custom_headers(response: Response):
    """Response with custom headers"""
    response.headers["X-Custom-Header"] = "CustomValue"
    response.headers["X-Request-ID"] = "12345"
    return {"message": "Response with custom headers"}

# Custom status codes
@app.get("/custom-status")
async def custom_status():
    """Return custom status code"""
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"message": "Request accepted for processing"}
    )

# HTML response
@app.get("/html", response_class=HTMLResponse)
async def get_html():
    """Return HTML response"""
    html_content = """
    <html>
        <head><title>FastAPI HTML</title></head>
        <body>
            <h1>Hello from FastAPI</h1>
            <p>This is an HTML response</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Redirect response
@app.get("/redirect")
async def redirect():
    """Redirect to another URL"""
    return RedirectResponse(url="/request-info", status_code=status.HTTP_302_FOUND)

# Streaming response
async def generate_data():
    """Generate data for streaming"""
    for i in range(100):
        yield f"data: {i}\n\n"

@app.get("/stream")
async def stream_data():
    """Stream data to client"""
    return StreamingResponse(generate_data(), media_type="text/event-stream")

# File download
@app.get("/download")
async def download_file():
    """Download file"""
    content = "Sample file content\nLine 2\nLine 3"
    file_like = io.BytesIO(content.encode())

    return StreamingResponse(
        file_like,
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=sample.txt"}
    )

# Cookies
@app.get("/set-cookie")
async def set_cookie(response: Response):
    """Set cookie"""
    response.set_cookie(
        key="session_id",
        value="abc123",
        max_age=3600,
        httponly=True,
        secure=True
    )
    return {"message": "Cookie set"}

@app.get("/read-cookie")
async def read_cookie(session_id: Optional[str] = Cookie(None)):
    """Read cookie"""
    if session_id:
        return {"session_id": session_id}
    return {"message": "No cookie found"}

# Request body
@app.post("/echo")
async def echo_request(request: Request):
    """Echo request body"""
    body = await request.body()
    return {"received": body.decode()}

# Custom response model
from pydantic import BaseModel

class CustomResponse(BaseModel):
    success: bool
    message: str
    data: dict

@app.get("/custom-response", response_model=CustomResponse)
async def get_custom_response():
    """Return custom response model"""
    return CustomResponse(
        success=True,
        message="Operation successful",
        data={"key": "value"}
    )
