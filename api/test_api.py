"""
Test script for the Video Highlights API.
Tests video upload, event retrieval, and chat functionality.
"""

import requests
import os
import json
import sys
from pathlib import Path
import logging

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from event_db import EventDB
from config import POSTGRES_URL, OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL

# Set up logging
log_dir = Path(project_root) / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "test_api.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API base URL
BASE_URL = "http://localhost:8000"

def test_root():
    """Test the root endpoint."""
    logger.info("Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        logger.info(f"Root endpoint response status: {response.status_code}")
        logger.info(f"Root endpoint response: {response.json()}")
        print("\nTesting root endpoint:")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
    except Exception as e:
        logger.error(f"Error testing root endpoint: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")

def test_video_upload(video_path):
    """Test video upload and processing."""
    logger.info(f"Testing video upload with: {video_path}")
    print(f"\nTesting video upload with: {video_path}")
    
    # Check if file exists
    if not os.path.exists(video_path):
        logger.error(f"File not found at {video_path}")
        print(f"Error: File not found at {video_path}")
        return None
    
    # Upload video
    try:
        with open(video_path, 'rb') as f:
            files = {'file': (os.path.basename(video_path), f, 'video/mp4')}
            logger.info(f"Sending file: {os.path.basename(video_path)}")
            print(f"Sending file: {os.path.basename(video_path)}")
            
            logger.debug("Making POST request to /api/video/upload")
            response = requests.post(f"{BASE_URL}/api/video/upload", files=files)
            logger.info(f"Upload response status: {response.status_code}")
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                logger.info("Upload successful")
                print("Upload successful!")
                print(f"Events saved: {result['events_saved']}")
                return result['filename']
            else:
                logger.error(f"Upload failed: {response.text}")
                print(f"Error: {response.text}")
                return None
    except Exception as e:
        logger.error(f"Exception during upload: {str(e)}", exc_info=True)
        print(f"Exception during upload: {str(e)}")
        return None

def test_get_events(video_filename):
    """Test retrieving events for a video."""
    logger.info(f"Testing event retrieval for: {video_filename}")
    print(f"\nTesting event retrieval for: {video_filename}")
    
    try:
        logger.debug(f"Making GET request to /api/video/events/{video_filename}")
        response = requests.get(f"{BASE_URL}/api/video/events/{video_filename}")
        logger.info(f"Events response status: {response.status_code}")
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            events = response.json()
            logger.info(f"Found {len(events)} events")
            print(f"Found {len(events)} events:")
            for event in events:
                print(f"- {event['description']}")
        else:
            logger.error(f"Error retrieving events: {response.text}")
            print(f"Error: {response.text}")
    except Exception as e:
        logger.error(f"Exception during event retrieval: {str(e)}", exc_info=True)
        print(f"Exception during event retrieval: {str(e)}")

def test_chat(query, limit=3):
    """Test chat functionality."""
    print(f"\nTesting chat with query: {query}")
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"query": query, "limit": limit}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Found {result['total_results']} relevant events:")
        for event in result['events']:
            print(f"- {event['description']} (similarity: {event['similarity']:.2f})")
    else:
        print(f"Error: {response.text}")

def test_database_contents(video_filename):
    """Test retrieving events directly from database."""
    logger.info(f"Testing database contents for: {video_filename}")
    print(f"\nTesting database contents for: {video_filename}")
    
    try:
        # Connect to database
        db = EventDB(
            db_url=POSTGRES_URL,
            openai_api_key=OPENAI_API_KEY,
            embedding_model=OPENAI_EMBEDDING_MODEL
        )
        
        # Get events by filename
        events = db.get_events_by_filename(video_filename)
        logger.info(f"Found {len(events)} events in database")
        
        print(f"\nFound {len(events)} events in database:")
        for event in events:
            print(f"\nEvent ID: {event['id']}")
            print(f"Timestamp: {event['timestamp']}")
            print(f"Description: {event['description']}")
            if event['llm_summary']:
                print(f"LLM Summary: {event['llm_summary']}")
            print("-" * 50)
            
        # Close database connection
        db.close()
        
    except Exception as e:
        logger.error(f"Exception during database check: {str(e)}", exc_info=True)
        print(f"Exception during database check: {str(e)}")

def main():
    """Run all tests."""
    logger.info("Starting API tests")
    
    # Test root endpoint
    test_root()
    
    # Get video path from user
    video_path = input("\nEnter path to test video file: ").strip()
    if not video_path:
        logger.warning("No video path provided")
        print("No video path provided. Exiting.")
        return
    
    # Test video upload
    video_filename = test_video_upload(video_path)
    if not video_filename:
        logger.error("Video upload failed")
        print("Video upload failed. Exiting.")
        return
    
    # Test database contents
    test_database_contents(video_filename)
    
    # Test event retrieval
    test_get_events(video_filename)
    
    # Test chat
    while True:
        query = input("\nEnter a chat query (or 'q' to quit): ").strip()
        if query.lower() == 'q':
            break
        test_chat(query)

    logger.info("API tests completed")

if __name__ == "__main__":
    main() 