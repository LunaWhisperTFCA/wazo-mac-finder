"""
Configuration management that reliably finds and loads the .env file.
"""
import os
from typing import Optional
from dotenv import load_dotenv

class Config:
    """
    Configuration class for Wazo API connection.
    It reliably finds and loads the .env file located in the same directory.
    """
    def __init__(self):
        """Initialize configuration from environment variables."""
        # Build an absolute path to the .env file to make it location-independent
        dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        
        # Load the .env file if it exists
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path=dotenv_path)
        
        self.host: Optional[str] = os.getenv('WAZO_HOST')
        self.token: Optional[str] = os.getenv('WAZO_TOKEN')
