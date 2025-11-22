#!/bin/bash
# Test script for AI Doctor Chatbot

set -e

echo "🧪 Running AI Doctor Chatbot Tests"
echo "===================================="
echo ""

# Activate virtual environment
if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
else
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

cd backend

# Run linting
echo "Running code quality checks..."
echo ""

echo "1. Black (code formatting)..."
black --check app/ || (echo "❌ Black formatting failed. Run: black app/" && exit 1)
echo "✓ Black check passed"
echo ""

echo "2. isort (import sorting)..."
isort --check-only app/ || (echo "❌ isort check failed. Run: isort app/" && exit 1)
echo "✓ isort check passed"
echo ""

echo "3. flake8 (linting)..."
flake8 app/ --max-line-length=100 --extend-ignore=E203,W503
echo "✓ flake8 check passed"
echo ""

echo "4. mypy (type checking)..."
mypy app/ --ignore-missing-imports || echo "⚠️  Type checking warnings (non-blocking)"
echo ""

# Run tests
echo "Running unit tests..."
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

echo ""
echo "===================================="
echo "✅ All tests passed!"
echo ""
echo "Coverage report generated in htmlcov/index.html"
echo "===================================="
