from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

from src.api.routes.email_routes import router as email_router
from src.api.routes.profile_routes import router as profile_router
from src.api.services.profile_service import ProfileService

app = FastAPI(
    title="AutoMail Agent API",
    description="A beautiful web interface for sending emails through Gmail automation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(email_router, prefix="/api")
app.include_router(profile_router, prefix="/api")

def get_profile_service() -> ProfileService:
    return ProfileService()

@app.get("/", response_class=HTMLResponse)
async def home() -> FileResponse:
    """Serve the main HTML page"""
    static_html_path = os.path.join(static_dir, "index.html")
    return FileResponse(static_html_path, media_type="text/html")

@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint"""
    return {"status": "healthy", "message": "AutoMail Agent API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 