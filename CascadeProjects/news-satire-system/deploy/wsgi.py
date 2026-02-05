#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from web.app import app

if __name__ == "__main__":
    app.run()
