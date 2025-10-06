#!/usr/bin/env python3
"""
Trade Tracker Application Runner
"""

import os
from app import app, db

if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        db.create_all()
        print("Database initialized successfully!")
    
    # Run the application
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting Trade Tracker on port {port}")
    print(f"Debug mode: {debug_mode}")
    print("Visit http://localhost:5000 to access the application")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)