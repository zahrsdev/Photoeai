"""
Main FastAPI application for the PhotoeAI backend.
Initializes the app, configures CORS, includes routers, and sets up structured logging.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
import sys
import os
from app.config.settings import settings
from app.routers.generator import router as generator_router

# Configure structured logging with Loguru
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    level="DEBUG" if settings.debug else "INFO",
    colorize=True
)

# Add file logging for production
logger.add(
    "logs/photoeai_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    level="INFO",
    rotation="1 day",
    retention="30 days",
    compression="zip"
)

logger.info("🚀 MISSION 3: Structured logging system initialized")

def cleanup_old_images():
    """Clean up image files older than 2 hours"""
    import time
    import glob
    
    image_dir = "static/images"
    if not os.path.exists(image_dir):
        return
        
    current_time = time.time()
    max_age = 2 * 3600  # 2 hours in seconds
    
    for image_file in glob.glob(os.path.join(image_dir, "img_*.png")):
        if os.path.getmtime(image_file) < (current_time - max_age):
            try:
                os.remove(image_file)
                logger.info(f"🗑️ Cleaned up old image: {image_file}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to cleanup {image_file}: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Replaces the deprecated @app.on_event decorators.
    """
    # Startup
    print("🚀 PhotoeAI Backend starting up...")
    print(f"📍 Environment: {'Development' if settings.debug else 'Production'}")
    print(f"🤖 OpenAI Model: {settings.openai_model}")
    
    # Cleanup old images on startup
    cleanup_old_images()
    
    print("✅ Startup completed successfully")
    
    yield  # Application runs here
    
    # Shutdown
    print("🛑 PhotoeAI Backend shutting down...")
    print("✅ Shutdown completed successfully")

# Create FastAPI application instance
app = FastAPI(
    title="PhotoeAI Backend",
    description="AI-powered backend engine for generating professional product photography briefs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Create static images directory if not exists
static_dir = "static/images"
os.makedirs(static_dir, exist_ok=True)

# Mount static files for serving generated images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
app.include_router(generator_router)


@app.get("/")
async def root():
    """
    Root endpoint providing basic API information.
    
    Returns:
        Dictionary with API information and health status
    """
    return {
        "message": "PhotoeAI Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs",
        "health_check": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the application with uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )
