from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Creating FastAPI app...")
app = FastAPI(
    title="Video Highlights Chat API",
    description="API for chatting about video highlights and processing videos",
    version="1.0.0"
)

logger.info("Configuring CORS...")
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Setting up root endpoint...")
@app.get("/")
async def root():
    """Root endpoint to verify API is running."""
    logger.info("Root endpoint called")
    return {"status": "ok", "message": "Video Highlights Chat API is running"}

# Add back video routes
logger.info("Importing video routes...")
from .routes import video
app.include_router(video.router, prefix="/api/video", tags=["video"])

# Add chat routes
logger.info("Importing chat routes...")
from .routes import chat
app.include_router(chat.router, prefix="/api", tags=["chat"])

logger.info("FastAPI app setup complete") 