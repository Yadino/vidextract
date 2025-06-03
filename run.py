import os
import sys
import json
from video_analyzer.analyze_video import AnalyzeVideo
from event_db import EventDB
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_EMBEDDING_MODEL, POSTGRES_URL, OUTPUT_DIR
from utils.logger import setup_logger

def main():
    # Setup logger first so we can use it for all messages
    logger = setup_logger("run")
    
    # Check command line arguments
    if len(sys.argv) != 2:
        logger.error("Usage: python run.py <video_path>")
        sys.exit(1)

    video_path = sys.argv[1]
    if not os.path.exists(video_path):
        logger.error(f"Video file not found at {video_path}")
        sys.exit(1)
    
    # Initialize video analyzer and database
    analyzer = AnalyzeVideo(OPENAI_API_KEY, OPENAI_MODEL, OUTPUT_DIR)
    db = EventDB(
        db_url=POSTGRES_URL,
        openai_api_key=OPENAI_API_KEY,
        embedding_model=OPENAI_EMBEDDING_MODEL
    )
    
    try:
        # Process video
        video_filename = os.path.basename(video_path)
        logger.info(f"Starting analysis of video: {video_filename}")
        results = analyzer.process_video(video_path)
        
        # Get LLM analysis
        logger.info("Getting LLM analysis of video")
        llm_analysis = analyzer.get_llm_analysis(results)
        
        # Print LLM analysis
        print("\nLLM Analysis:")
        print(json.dumps(llm_analysis, indent=2))
        
        # Save events to database
        logger.info("Saving events to database")
        saved_ids = db.save_llm_analysis(llm_analysis, video_filename)
        logger.info(f"Successfully saved {len(saved_ids)} events to database")
        
    except Exception as e:
        logger.error("An error occurred during video processing", exc_info=True)
        raise
    finally:
        # Cleanup
        db.close()
        logger.info("Processing completed")

if __name__ == "__main__":
    main() 