#!/bin/bash

# Trade Tracker Installation Script

echo "🚀 Installing Trade Tracker..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

# Create virtual environment (optional but recommended)
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
else
    echo "✅ .env file already exists"
fi

# Initialize database
echo "🗄️ Initializing database..."
python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
print('Database initialized successfully!')
"

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. (Optional) Set up GitHub OAuth for data syncing"
echo "3. Run the application: python3 run.py"
echo "4. Visit http://localhost:5000 to access the application"
echo ""
echo "📚 For detailed instructions, see README.md"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "source venv/bin/activate"