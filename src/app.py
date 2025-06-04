from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from src.schemas.config import config
from src.core.logger import get_logger
from src.routes.email_routes import router as email_router
from src.routes.profile_routes import router as profile_router
from src.core.dependencies import get_profile_service

logger = get_logger(__name__)

app = FastAPI(
    title="AutoMail Agent API",
    description="A beautiful web interface for sending emails through Gmail automation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

app.include_router(email_router)
app.include_router(profile_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Serve the main HTML page with configuration values"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_title": config.app_title,
        "app_description": config.app_description,
        "default_headless": config.headless
    })

@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint"""
    logger.info("Health check requested")
    return {
        "status": "healthy", 
        "message": "AutoMail Agent API is running",
        "environment": config.environment.value
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.host, port=config.port) 