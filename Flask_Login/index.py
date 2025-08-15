#!/usr/bin/env python3
"""
Entry point for Railway deployment
This file ensures Railway can find and run the Flask application
"""

from app import app
import os

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
