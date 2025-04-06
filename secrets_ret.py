"""
Module for retrieving secrets in a Cloud Run-compatible way.
Tries to get secrets from environment variables first, then loads from .env file for local development.
"""
import os
import sys
from typing import Optional
from pathlib import Path

# Try to import dotenv, but don't fail if it's not installed
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# Load environment variables from .env file if running locally
if DOTENV_AVAILABLE:
    # Find the project root directory (where the .env file should be located)
    current_file = Path(__file__).resolve()
    project_root = current_file.parent  # .env should be in same directory as this file
    
    # Look for .env file and load it if it exists
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"INFO: Loaded environment variables from {env_path}")
    else:
        print(f"INFO: No .env file found at {env_path}, using system environment variables")

def get_secret(secret_name: str) -> Optional[str]:
    """
    Get a secret by name from the environment or other sources.
    
    In production (like Cloud Run), secrets should be passed as environment variables.
    In local development, secrets can be stored in a .env file.
    
    Args:
        secret_name: Name of the secret to retrieve
        
    Returns:
        The secret value if found, None otherwise
    """
    # Try to get from environment variable directly
    secret_value = os.environ.get(secret_name)
    if secret_value:
        return secret_value
    
    # If we're here, the secret wasn't found
    print(f"WARNING: Secret {secret_name} not found in environment variables or .env file")
    return None
