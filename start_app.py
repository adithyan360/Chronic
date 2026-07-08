#!/usr/bin/env python3
"""
Simple startup script for ProgressionPred
"""

import os
import sys

def main():
    print("=" * 60)
    print("🏥 PROGRESSIONPRED - CHRONIC DISEASE TRACKER")
    print("=" * 60)
    
    # Initialize database
    print("📊 Initializing database...")
    from app import init_db
    init_db()
    
    print("✅ Database ready!")
    print("🚀 Starting application...")
    print("\n📱 Open your browser and go to: http://localhost:5000")
    print("👤 Demo Login: username=demo, password=demo123")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 60)
    
    # Start Flask app
    os.system("python app.py")

if __name__ == "__main__":
    main()