"""
Pydantic models for the chat API.

This module defines the data structures used in the chat API:
- Event: Represents a video event with its metadata and similarity score
- ChatRequest: Represents an incoming chat query
- ChatResponse: Represents the API response with matching events
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Event(BaseModel):
    """
    Represents a video event with its metadata and similarity score.
    
    Attributes:
        id: Unique identifier for the event
        timestamp: Timestamp of the event in seconds (float)
        description: Text description of the event
        video_id: ID of the source video
        video_filename: Original filename of the video
        llm_summary: Optional additional summary from LLM
        similarity: Cosine similarity score for search results, optional when retrieving all events
    """
    id: int
    timestamp: float
    description: str
    video_id: str
    video_filename: str
    llm_summary: Optional[str] = None
    similarity: Optional[float] = None

class ChatRequest(BaseModel):
    """
    Represents an incoming chat query.
    
    Attributes:
        query: The natural language query from the user
        limit: Optional maximum number of results to return (default: 5)
        video_filename: The filename of the video the chat is about
    """
    query: str
    limit: Optional[int] = 5
    video_filename: str

class ChatResponse(BaseModel):
    """
    Represents the API response with matching events.
    
    Attributes:
        events: List of matching Event objects
        total_results: Total number of events found
    """
    events: List[Event]
    total_results: int 