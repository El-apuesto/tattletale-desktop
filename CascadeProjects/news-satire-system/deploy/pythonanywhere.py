#!/usr/bin/env python3
"""
Deployment script for PythonAnywhere
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from web.app import app

# PythonAnywhere specific configuration
if __name__ == '__main__':
    # Use the port provided by PythonAnywhere
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
