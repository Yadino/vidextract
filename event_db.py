import os
import psycopg2
from psycopg2.extras import Json
from datetime import datetime
import numpy as np
from openai import OpenAI
from utils.logger import setup_logger

class EventDB:
    def __init__(self, db_url, openai_api_key, embedding_model):
        """
        Initialize the EventDB with database connection and OpenAI client.
        
        Parameters:
            db_url (str): PostgreSQL connection URL
            openai_api_key (str): OpenAI API key for generating embeddings
            embedding_model (str): OpenAI model to use for embeddings
        """
        self.logger = setup_logger("event_db")
        self.conn = psycopg2.connect(db_url)
        self.client = OpenAI(api_key=openai_api_key)
        self.embedding_model = embedding_model
        
        # Create the table if it doesn't exist
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables and extensions if they don't exist."""
        with self.conn.cursor() as cur:
            # Enable pgvector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create events table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id SERIAL PRIMARY KEY,
                    timestamp DOUBLE PRECISION NOT NULL,
                    description TEXT NOT NULL,
                    video_id TEXT NOT NULL,
                    video_filename TEXT NOT NULL,
                    embedding vector(1536),
                    llm_summary TEXT
                );
                
                -- Create index on video_id and video_filename for faster lookups
                CREATE INDEX IF NOT EXISTS idx_events_video_id ON events(video_id);
                CREATE INDEX IF NOT EXISTS idx_events_video_filename ON events(video_filename);
            """)
            self.conn.commit()
            self.logger.info("Database tables and indexes created/verified")
    
    def _get_embedding(self, text):
        """
        Get embedding for text using OpenAI's API.
        
        Parameters:
            text (str): Text to generate embedding for
            
        Returns:
            list: Embedding vector
        """
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
    
    def save_event(self, timestamp, description, video_id, video_filename, llm_summary=None):
        """
        Save an event to the database with its embedding.
        
        Parameters:
            timestamp (datetime): When the event occurred
            description (str): Description of the event
            video_id (str): ID of the video this event is from
            video_filename (str): Original filename of the video
            llm_summary (str, optional): Additional LLM-generated summary
        """
        # Generate embedding for the description
        embedding = self._get_embedding(description)
        
        with self.conn.cursor() as cur:
            self.logger.debug(f"save_event: Received timestamp={timestamp} (type={type(timestamp)})")
            cur.execute("""
                INSERT INTO events (timestamp, description, video_id, video_filename, embedding, llm_summary)
                VALUES (%s, %s, %s, %s, %s::vector, %s)
                RETURNING id;
            """, (timestamp, description, video_id, video_filename, embedding, llm_summary))
            
            event_id = cur.fetchone()[0]
            self.conn.commit()
            self.logger.debug(f"Saved event {event_id} for video {video_filename}")
            return event_id

    def save_llm_analysis(self, llm_analysis, video_filename):
        """
        Save multiple events from LLM analysis to the database.
        
        Parameters:
            llm_analysis (dict): The LLM analysis containing moments
            video_filename (str): Original filename of the video
            
        Returns:
            list: List of saved event IDs
        """
        if not llm_analysis or "moments" not in llm_analysis:
            self.logger.warning("No moments found in LLM analysis")
            return []
            
        video_id = os.path.splitext(video_filename)[0]
        saved_ids = []
        
        for i, moment in enumerate(llm_analysis["moments"]):
            try:
                # Check for required fields
                required_fields = ["start_time", "end_time", "description"]
                missing_fields = [field for field in required_fields if field not in moment]
                if missing_fields:
                    self.logger.warning(f"Moment {i} is missing required fields: {missing_fields}, skipping")
                    continue
                
                # Use start_time directly as seconds (float)
                timestamp_seconds = float(moment["start_time"])
                self.logger.debug(f"Processing moment {i}: start_time={moment['start_time']} (type={type(moment['start_time'])}) -> timestamp_seconds={timestamp_seconds}")
                
                # Save event
                event_id = self.save_event(
                    timestamp=timestamp_seconds,
                    description=moment["description"],
                    video_id=video_id,
                    video_filename=video_filename,
                    llm_summary=moment.get("summary")  # Optional field
                )
                saved_ids.append(event_id)
                
            except (ValueError, TypeError) as e:
                # Catch errors related to timestamp conversion
                self.logger.error(f"Timestamp conversion error for moment {i}: {e}", exc_info=True)
                continue
            except Exception as e:
                # Catch any other general exceptions during saving
                self.logger.error(f"Error saving moment {i}: {e}", exc_info=True)
                continue
            
        self.logger.info(f"Saved {len(saved_ids)} events to database for video {video_filename}")
        return saved_ids
    
    def get_events_by_video_id(self, video_id):
        """
        Get all events for a specific video ID.
        
        Parameters:
            video_id (str): The video ID to search for
            
        Returns:
            list: List of event dictionaries
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, timestamp, description, video_id, video_filename, llm_summary
                FROM events
                WHERE video_id = %s
                ORDER BY timestamp;
            """, (video_id,))
            
            events = []
            for row in cur.fetchall():
                events.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'description': row[2],
                    'video_id': row[3],
                    'video_filename': row[4],
                    'llm_summary': row[5]
                })
            self.logger.info(f"Retrieved {len(events)} events for video ID {video_id}")
            return events
    
    def get_events_by_filename(self, video_filename):
        """
        Get all events for a specific video filename.
        
        Parameters:
            video_filename (str): The video filename to search for
            
        Returns:
            list: List of event dictionaries
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, timestamp, description, video_id, video_filename, llm_summary
                FROM events
                WHERE video_filename = %s
                ORDER BY timestamp;
            """, (video_filename,))
            
            events = []
            for row in cur.fetchall():
                events.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'description': row[2],
                    'video_id': row[3],
                    'video_filename': row[4],
                    'llm_summary': row[5]
                })
            self.logger.info(f"Retrieved {len(events)} events for video {video_filename}")
            return events
    
    def close(self):
        """Close the database connection."""
        self.conn.close()
        self.logger.info("Database connection closed")

    def search_events(self, query, limit=5):
        """
        Search events using semantic similarity.
        
        Parameters:
            query (str): The search query
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of matching event dictionaries with similarity scores
        """
        # Generate embedding for the query
        query_embedding = self._get_embedding(query)
        
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    id, 
                    timestamp, 
                    description, 
                    video_id, 
                    video_filename, 
                    llm_summary,
                    1 - (embedding <=> %s::vector) as similarity
                FROM events
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """, (query_embedding, query_embedding, limit))
            
            events = []
            for row in cur.fetchall():
                events.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'description': row[2],
                    'video_id': row[3],
                    'video_filename': row[4],
                    'llm_summary': row[5],
                    'similarity': float(row[6])
                })
            self.logger.info(f"Found {len(events)} events matching query")
            return events

    def reset_database(self):
        """Drop and recreate all tables."""
        with self.conn.cursor() as cur:
            # Drop existing tables
            cur.execute("DROP TABLE IF EXISTS events;")
            self.conn.commit()
            self.logger.info("Dropped existing tables")
            
            # Recreate tables
            self._create_tables()
            self.logger.info("Recreated tables") 