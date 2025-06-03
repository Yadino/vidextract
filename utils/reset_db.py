"""
Script to reset the database by dropping and recreating tables.
This is useful when we need to change the schema or fix data type issues.
"""

import sys
import os

# Add parent directory to path so we can import from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from event_db import EventDB
from config import POSTGRES_URL, OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL

def main():
    print("Connecting to database...")
    db = EventDB(POSTGRES_URL, OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL)
    
    print("Resetting database...")
    db.reset_database()
    
    print("Closing database connection...")
    db.close()
    
    print("Database reset complete!")

if __name__ == "__main__":
    main() 