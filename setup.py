#!/usr/bin/env python3
"""
Setup script for Trade Tracker
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    print("🚀 Setting up Trade Tracker...")
    
    # Check if Python is available
    if not run_command("python3 --version", "Checking Python version"):
        print("❌ Python 3 is required but not found. Please install Python 3.")
        sys.exit(1)
    
    # Install requirements
    if not run_command("pip3 install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("""# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE_URL=sqlite:///trades.db

# GitHub OAuth Configuration (Optional)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# GitHub Repository Configuration
GITHUB_REPO_OWNER=your-github-username
GITHUB_REPO_NAME=trade-tracker-data
""")
        print("✅ .env file created. Please edit it with your configuration.")
    else:
        print("✅ .env file already exists")
    
    # Initialize database
    print("🗄️ Initializing database...")
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. (Optional) Set up GitHub OAuth for data syncing")
    print("3. Run the application: python3 run.py")
    print("4. Visit http://localhost:5000 to access the application")
    print("\n📚 For detailed instructions, see README.md")

if __name__ == '__main__':
    main()