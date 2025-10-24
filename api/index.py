"""
Vercel serverless entry point for the Flask app.
This file is required for Vercel Python deployment.
"""
import sys
import os

# Add the project root to Python path so we can import from src/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app

# Vercel will call this 'app' object
# The Flask app is already configured in src/main.py
