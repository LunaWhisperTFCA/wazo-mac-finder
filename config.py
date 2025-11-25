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
        
        self.servers = self._load_servers()

    def _load_servers(self):
        """Load all Wazo server configurations from environment variables."""
        servers = []
        
        # Check for the primary server (no suffix)
        host = os.getenv('WAZO_HOST')
        token = os.getenv('WAZO_TOKEN')
        if host and token:
            servers.append({'host': host, 'token': token, 'name': 'Server 1'})

        # Check for additional servers (WAZO_HOST2, WAZO_HOST3, etc.)
        i = 2
        while True:
            host = os.getenv(f'WAZO_HOST{i}')
            token = os.getenv(f'WAZO_TOKEN{i}')
            
            if not (host and token):
                break
            
            servers.append({'host': host, 'token': token, 'name': f'Server {i}'})
            i += 1
            
        return servers
