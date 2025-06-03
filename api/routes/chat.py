"""
Chat API routes for video highlights.

This module provides the FastAPI routes for the chat functionality:
- POST /api/chat: Search for video events based on natural language queries
- Database connection management
- Error handling for chat operations
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from api.models.chat import ChatRequest, ChatResponse, Event
from event_db import EventDB
from config import POSTGRES_URL, OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL

router = APIRouter()

def get_db():
    """
    Dependency to get database connection.
    
    Creates and yields a database connection, ensuring it's properly closed after use.
    Uses configuration from environment variables.
    
    Yields:
        EventDB: Database connection instance
    """
    db = EventDB(
        db_url=POSTGRES_URL,
        openai_api_key=OPENAI_API_KEY,
        embedding_model=OPENAI_EMBEDDING_MODEL
    )
    try:
        yield db
    finally:
        db.close()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: EventDB = Depends(get_db)):
    """
    Search for events based on a natural language query.
    
    This endpoint performs semantic search on the video events database
    using cosine similarity between the query and event descriptions.
    
    Parameters:
        request: ChatRequest containing the query and optional limit
        db: Database connection (injected by FastAPI)
    
    Returns:
        ChatResponse containing matching events and total count
    
    Raises:
        HTTPException: If there's an error during the search
    """
    try:
        if request.query == '__GET_ALL_EVENTS__':
            # If query is the special marker, get all events by filename
            events = db.get_events_by_filename(request.video_filename)
        else:
            # Otherwise, perform a semantic search
            events = db.search_events(request.query, request.limit)
        return ChatResponse(
            events=[Event(**event) for event in events],
            total_results=len(events)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 