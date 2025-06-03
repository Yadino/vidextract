import os
import sys
import uvicorn
import logging
from pathlib import Path

# Set up logging to both file and console
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
log_dir = Path(project_root) / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "api.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add the project root directory to Python path
sys.path.insert(0, project_root)

logger.info(f"Project root: {project_root}")
logger.info("Starting FastAPI server...")

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="debug"  # Enable debug logging
    ) 