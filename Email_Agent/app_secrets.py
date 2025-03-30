"""
App secrets module for loading environment variables
Renamed to avoid conflict with Python's built-in secrets module
"""
from dotenv import load_dotenv
import os

load_dotenv()  # This loads the variables from .env

def get_secret(secret_name):
    """
    Get a secret from environment variables
    """
    return os.getenv(secret_name)
