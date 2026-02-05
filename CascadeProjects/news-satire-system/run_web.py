#!/usr/bin/env python3
"""
Launch the web interface for The Satire Chronicle
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from web.app import app

if __name__ == '__main__':
    print("🌐 Starting The Satire Chronicle web interface...")
    print("📍 Open your browser to: http://localhost:5000")
    print("✨ Luxury news satire meets high fashion!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
