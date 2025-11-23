#!/bin/bash
# Setup script for AI Doctor Chatbot

set -e  # Exit on error

echo "🏥 AI Doctor Chatbot - Setup Script"
echo "===================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required. You have $python_version"
    exit 1
fi
echo "✓ Python $python_version detected"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
cd backend
python3 -m venv venv
echo "✓ Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Copy environment file
echo ""
if [ ! -f "../.env" ]; then
    echo "Creating .env file..."
    cp ../.env.example ../.env
    echo "✓ .env file created"
    echo "⚠️  Please edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - SECRET_KEY"
    echo "   - Other configuration as needed"
else
    echo "✓ .env file already exists"
fi

# Setup database
echo ""
echo "Database setup..."
echo "Please ensure PostgreSQL is running and create database:"
echo "  createdb doctor_assistant"
read -p "Press enter when database is ready..."

# Setup Redis
echo ""
echo "Redis setup..."
echo "Please ensure Redis is running"
read -p "Press enter when Redis is ready..."

# Setup Qdrant
echo ""
echo "Qdrant setup..."
echo "Starting Qdrant with Docker..."
docker run -d -p 6333:6333 -p 6334:6334 -v $(pwd)/../data/qdrant:/qdrant/storage qdrant/qdrant
echo "✓ Qdrant started"

# Run migrations (when implemented)
# echo ""
# echo "Running database migrations..."
# alembic upgrade head
# echo "✓ Migrations completed"

echo ""
echo "===================================="
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Activate virtual environment: source backend/venv/bin/activate"
echo "3. Run the application: uvicorn app.main:app --reload"
echo "4. Visit http://localhost:8000/api/docs for API documentation"
echo ""
echo "For Docker deployment: docker-compose up -d"
echo "===================================="
