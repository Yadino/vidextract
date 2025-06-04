"""
Configuration settings for the video analyzer.
"""

import os
from pathlib import Path

# Base paths
ROOT_DIR = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "output"

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", 
                           "<default API key>")  # Get from environment variable or use default
OPENAI_MODEL = "gpt-4o-mini"  # The model to use for analysis
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"  # The model to use for embeddings

# Database Configuration
POSTGRES_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/vidextract")

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(exist_ok=True) 
