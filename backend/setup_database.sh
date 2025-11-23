#!/bin/bash

# Fitness Assistant - Database Setup Script
# This script sets up PostgreSQL database from scratch

set -e  # Exit on error

echo "🏋️  Fitness Assistant - Database Setup"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default values
DB_USER=${POSTGRES_USER:-fitness_user}
DB_PASSWORD=${POSTGRES_PASSWORD:-fitness_pass}
DB_NAME=${POSTGRES_DB:-fitness_assistant}
DB_HOST=${POSTGRES_HOST:-localhost}
DB_PORT=${POSTGRES_PORT:-5432}

# Check if .env exists
if [ -f .env ]; then
    echo -e "${GREEN}✓${NC} Found .env file, loading credentials..."
    source .env
    DB_USER=$POSTGRES_USER
    DB_PASSWORD=$POSTGRES_PASSWORD
    DB_NAME=$POSTGRES_DB
    DB_HOST=$POSTGRES_HOST
    DB_PORT=$POSTGRES_PORT
else
    echo -e "${YELLOW}⚠${NC}  No .env file found. Using defaults."
    echo "   Database: $DB_NAME"
    echo "   User: $DB_USER"
    echo "   Host: $DB_HOST:$DB_PORT"
    echo ""
    read -p "Continue with defaults? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please create a .env file first. Copy from .env.example"
        exit 1
    fi
fi

echo ""
echo "Step 1: Checking PostgreSQL..."
echo "==============================="

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}✗${NC} PostgreSQL is not installed!"
    echo "Install with: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi
echo -e "${GREEN}✓${NC} PostgreSQL is installed"

# Check if PostgreSQL is running
if ! pg_isready -h $DB_HOST -p $DB_PORT &> /dev/null; then
    echo -e "${YELLOW}⚠${NC}  PostgreSQL is not running"
    echo "Attempting to start..."

    # Try different methods to start PostgreSQL
    if command -v systemctl &> /dev/null; then
        sudo systemctl start postgresql || true
    elif command -v service &> /dev/null; then
        sudo service postgresql start || true
    else
        echo -e "${YELLOW}⚠${NC}  Could not start PostgreSQL automatically"
        echo "Please start PostgreSQL manually and run this script again"
        exit 1
    fi

    # Wait a bit for PostgreSQL to start
    sleep 2

    # Check again
    if ! pg_isready -h $DB_HOST -p $DB_PORT &> /dev/null; then
        echo -e "${RED}✗${NC} PostgreSQL is still not running"
        echo "Please start PostgreSQL manually:"
        echo "  sudo systemctl start postgresql"
        echo "  or"
        echo "  docker run --name postgres-fitness -e POSTGRES_PASSWORD=$DB_PASSWORD -p 5432:5432 -d postgres:15"
        exit 1
    fi
fi
echo -e "${GREEN}✓${NC} PostgreSQL is running"

echo ""
echo "Step 2: Creating database and user..."
echo "======================================"

# Create user and database using postgres superuser
sudo -u postgres psql <<EOF
-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
        RAISE NOTICE 'User $DB_USER created';
    ELSE
        RAISE NOTICE 'User $DB_USER already exists';
    END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

\c $DB_NAME

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO $DB_USER;
GRANT ALL ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Database and user configured"
else
    echo -e "${RED}✗${NC} Failed to create database/user"
    echo ""
    echo "Alternative: Try using Docker PostgreSQL:"
    echo "  docker run --name postgres-fitness \\"
    echo "    -e POSTGRES_USER=$DB_USER \\"
    echo "    -e POSTGRES_PASSWORD=$DB_PASSWORD \\"
    echo "    -e POSTGRES_DB=$DB_NAME \\"
    echo "    -p 5432:5432 \\"
    echo "    -d postgres:15"
    exit 1
fi

echo ""
echo "Step 3: Running Alembic migrations..."
echo "======================================"

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
    echo -e "${YELLOW}⚠${NC}  Alembic not installed. Installing..."
    pip install alembic psycopg2-binary pydantic pydantic-settings python-dotenv
fi

# Run migrations
export POSTGRES_USER=$DB_USER
export POSTGRES_PASSWORD=$DB_PASSWORD
export POSTGRES_DB=$DB_NAME
export POSTGRES_HOST=$DB_HOST
export POSTGRES_PORT=$DB_PORT
export SECRET_KEY=${SECRET_KEY:-your-super-secret-key-for-setup-only-change-this-in-production}

alembic upgrade head

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Migrations applied successfully"
else
    echo -e "${RED}✗${NC} Migration failed"
    exit 1
fi

echo ""
echo "Step 4: Verifying database schema..."
echo "======================================"

# Verify tables were created
TABLES=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

if [ "$TABLES" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Database schema created ($TABLES tables)"

    # List tables
    echo ""
    echo "Tables created:"
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\dt" | grep public
else
    echo -e "${RED}✗${NC} No tables found"
    exit 1
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Host: $DB_HOST:$DB_PORT"
echo ""
echo "Next steps:"
echo "1. Start the backend:  uvicorn app.main:app --reload"
echo "2. Start the frontend: cd ../frontend && npm start"
echo ""
echo "🎉 Your Fitness Assistant is ready!"
