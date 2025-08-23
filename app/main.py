"""
Main FastAPI application for the PhotoeAI backend.
Initializes the app, configures CORS, includes routers, and sets up structured logging.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys
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
