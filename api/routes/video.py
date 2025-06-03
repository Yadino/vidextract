"""
Video processing routes for the API.

This module provides endpoints for:
- Uploading and processing videos
- Getting analysis results
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
from api.models.chat import Event
import logging
import os
from pathlib import Path
from video_analyzer.analyze_video import AnalyzeVideo
from event_db import EventDB
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_EMBEDDING_MODEL, POSTGRES_URL, OUTPUT_DIR

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def get_db():
    """Get database connection."""
    db = EventDB(
        db_url=POSTGRES_URL,
        openai_api_key=OPENAI_API_KEY,
        embedding_model=OPENAI_EMBEDDING_MODEL
    )
    try:
        yield db
    finally:
        db.close()

@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    db: EventDB = Depends(get_db)
):
    """
    Upload and process a video file.
    
    Parameters:
        file: The video file to upload
        db: Database connection (injected by FastAPI)
    
    Returns:
        dict: Processing results
    """
    temp_path = None
    try:
        logger.info(f"Received upload request for file: {file.filename}")
        
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Save uploaded file temporarily
        temp_path = OUTPUT_DIR / file.filename
        logger.info(f"Saving uploaded file to: {temp_path}")
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Initialize video analyzer
        analyzer = AnalyzeVideo(OPENAI_API_KEY, OPENAI_MODEL, OUTPUT_DIR)
        
        # Process video
        logger.info(f"Starting analysis of video: {file.filename}")
        results = analyzer.process_video(str(temp_path))
        
        # Get LLM analysis
        logger.info("Getting LLM analysis of video")
        llm_analysis = analyzer.get_llm_analysis(results)
        
        # Save events to database
        logger.info("Saving events to database")
        saved_ids = db.save_llm_analysis(llm_analysis, file.filename)
        
        return {
            "message": "File processed successfully",
            "filename": file.filename,
            "events_saved": len(saved_ids),
            "analysis": llm_analysis
        }
        
    except Exception as e:
        logger.error(f"Error in upload_video: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.info(f"Cleaned up temporary file: {temp_path}")
            except Exception as e:
                logger.error(f"Error cleaning up temporary file: {str(e)}", exc_info=True)

@router.get("/events/{video_filename}", response_model=List[Event])
async def get_video_events(
    video_filename: str,
    db: EventDB = Depends(get_db)
):
    """
    Get all events for a specific video.
    
    Parameters:
        video_filename: Name of the video file
        db: Database connection (injected by FastAPI)
    
    Returns:
        List[Event]: List of events for the video
    """
    try:
        logger.info(f"Received request for events of video: {video_filename}")
        events = db.get_events_by_filename(video_filename)
        logger.info(f"Found {len(events)} events in database")
        
        # Convert events to Event model
        event_models = []
        for event in events:
            try:
                event_models.append(Event(
                    id=event['id'],
                    timestamp=event['timestamp'],
                    description=event['description'],
                    video_id=event['video_id'],
                    video_filename=event['video_filename'],
                    llm_summary=event['llm_summary'],
                    similarity=1.0  # Default similarity for direct database queries
                ))
            except Exception as e:
                logger.error(f"Error converting event to model: {str(e)}", exc_info=True)
                continue
        
        return event_models
    except Exception as e:
        logger.error(f"Error in get_video_events: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 