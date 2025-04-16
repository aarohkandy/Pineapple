"""
Application settings for the AI agent.
"""
import os

# API configuration
API_KEY_ENV = "OPENROUTER_API_KEY"
API_BASE_URL = "https://openrouter.ai/api/v1"

# Application settings
APP_NAME = "AIAgent"
APP_VERSION = "0.1.0"
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# UI settings
UI_THEME = "light"
UI_FONT_SIZE = 14

# Timeout settings (in seconds)
MODEL_REQUEST_TIMEOUT = 120
CODE_EXECUTION_TIMEOUT = 10

# File paths
TEMP_DIR = os.path.join(os.path.expanduser("~"), ".aiagent", "temp")
OUTPUT_DIR = os.path.join(os.path.expanduser("~"), ".aiagent", "output")

# Create directories if they don't exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)