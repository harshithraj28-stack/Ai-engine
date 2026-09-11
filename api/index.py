"""Vercel Serverless Function entrypoint for ResQ-Verse."""

import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import app

# Vercel WSGI entry handler
app = app
