# Database Setup From Scratch

Complete guide to set up PostgreSQL and run Alembic migrations for the Fitness Assistant.

---

## 🗄️ Step 1: Start PostgreSQL

PostgreSQL is installed but needs to be started:

```bash
# Option 1: Using systemctl (if you have sudo)
sudo systemctl start postgresql
sudo systemctl enable postgresql  # Start on boot

# Option 2: Using pg_ctl (if systemctl doesn't work)
# First, find the data directory
pg_config --sysconfdir

# Then start PostgreSQL
pg_ctl -D /var/lib/postgresql/data start

# Option 3: Using Docker (alternative if native doesn't work)
docker run --name postgres-fitness \
  -e POSTGRES_USER=fitness_user \
  -e POSTGRES_PASSWORD=fitness_pass \
  -e POSTGRES_DB=fitness_assistant \
  -p 5432:5432 \
  -d postgres:15
```

### Verify PostgreSQL is Running

```bash
pg_isready
# Should output: /var/run/postgresql:5432 - accepting connections
```

---

## 👤 Step 2: Create Database User and Database

### Option A: Using psql (Recommended)

```bash
# Connect as postgres superuser
sudo -u postgres psql

# Or if sudo doesn't work:
psql -U postgres
```

Once in psql, run these commands:

```sql
-- Create a new user for the fitness assistant
CREATE USER fitness_user WITH PASSWORD 'your_secure_password_here';

-- Create the database
CREATE DATABASE fitness_assistant OWNER fitness_user;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE fitness_assistant TO fitness_user;

-- Connect to the new database
\c fitness_assistant

-- Grant schema privileges (needed for migrations)
GRANT ALL ON SCHEMA public TO fitness_user;

-- Exit psql
\q
```

### Option B: Using Docker (If you used Docker in Step 1)

The database and user are already created! Skip to Step 3.

---

## 🔧 Step 3: Configure Environment Variables

Create your `.env` file:

```bash
cd /home/user/doctor_assistant-/backend

# Copy the example
cp .env.example .env
```

Edit `.env` with your database credentials:

```bash
nano .env  # or use your preferred editor
```

**Minimum required settings:**

```env
# Database (CRITICAL - update these!)
POSTGRES_USER=fitness_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fitness_assistant

# Security (CRITICAL - change this!)
SECRET_KEY=your-super-secret-key-at-least-32-characters-long-change-this-now

# LLM APIs (Required for the assistant to work)
OPENAI_API_KEY=sk-your-openai-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Application
APP_NAME=Fitness & Nutrition Assistant
ENVIRONMENT=development
DEBUG=True
```

**If using Docker PostgreSQL, use these instead:**

```env
POSTGRES_USER=fitness_user
POSTGRES_PASSWORD=fitness_pass
POSTGRES_HOST=localhost  # or 127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=fitness_assistant
```

---

## 🚀 Step 4: Run Alembic Migrations

Now apply the database schema:

```bash
cd /home/user/doctor_assistant-/backend

# Verify Alembic can connect
alembic current

# Run the migration to create tables
alembic upgrade head
```

**Expected output:**

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001_fitness_nutrition, Add fitness and nutrition profile fields
```

---

## ✅ Step 5: Verify Database Schema

Check that tables were created:

```bash
# Connect to the database
psql -U fitness_user -d fitness_assistant -h localhost

# Or if using Docker:
docker exec -it postgres-fitness psql -U fitness_user -d fitness_assistant
```

In psql, run:

```sql
-- List all tables
\dt

-- Should show:
--  public | alembic_version      | table | fitness_user
--  public | health_profiles      | table | fitness_user
--  public | users                | table | fitness_user
--  public | conversations        | table | fitness_user
--  public | messages             | table | fitness_user
--  public | knowledge_documents  | table | fitness_user
--  (and more...)

-- Check health_profiles columns
\d health_profiles

-- You should see all the new fitness columns:
--   fitness_level
--   training_experience
--   fitness_goals
--   available_equipment
--   training_days_per_week
--   training_duration_minutes
--   current_injuries
--   health_conditions
--   diet_preference
--   dietary_restrictions
--   food_allergies
--   body_fat_percentage
--   body_measurements

-- Exit
\q
```

---

## 🎯 Step 6: Start the Application

```bash
cd /home/user/doctor_assistant-/backend

# Install dependencies if not already installed
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 🧪 Step 7: Test the API

Open a new terminal and test:

```bash
# Health check
curl http://localhost:8000/health

# API docs (open in browser)
# http://localhost:8000/docs
```

---

## 🎨 Step 8: Start the Frontend

```bash
cd /home/user/doctor_assistant-/frontend

# Install dependencies (if not done)
npm install

# Start the development server
npm start
```

The app should open at `http://localhost:3000`

---

## 🔍 Troubleshooting

### "Connection refused" when running Alembic

**Problem**: PostgreSQL isn't running

**Solution**:
```bash
# Check if running
pg_isready

# Start PostgreSQL
sudo systemctl start postgresql
# or
docker start postgres-fitness
```

### "FATAL: role 'fitness_user' does not exist"

**Problem**: Database user wasn't created

**Solution**: Go back to Step 2 and create the user

### "FATAL: database 'fitness_assistant' does not exist"

**Problem**: Database wasn't created

**Solution**:
```bash
sudo -u postgres psql -c "CREATE DATABASE fitness_assistant OWNER fitness_user;"
```

### "FATAL: password authentication failed"

**Problem**: Password in `.env` doesn't match database

**Solution**:
- Check your `.env` file has the correct `POSTGRES_PASSWORD`
- Or reset the password:
  ```sql
  ALTER USER fitness_user WITH PASSWORD 'new_password';
  ```

### "Module not found" errors

**Problem**: Dependencies not installed

**Solution**:
```bash
pip install pydantic pydantic-settings python-dotenv psycopg2-binary alembic
```

---

## 📊 Database Schema Overview

After migration, you'll have these main tables:

1. **users** - User accounts and authentication
2. **health_profiles** - User fitness profiles (with 12 new fitness fields!)
3. **conversations** - Chat conversation threads
4. **messages** - Individual messages in conversations
5. **knowledge_documents** - RAG knowledge base
6. **alembic_version** - Migration tracking

---

## 🔄 Future Migrations

When the schema needs to change:

```bash
# Create new migration (auto-detect changes)
alembic revision --autogenerate -m "Description of change"

# Review the generated file in alembic/versions/

# Apply the migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

---

## 🎉 You're All Set!

Once you complete these steps, you'll have:

✅ PostgreSQL running
✅ Database and user created
✅ All tables created with fitness fields
✅ Backend API running
✅ Frontend ready to test

Your fitness and nutrition assistant is ready to use! 🏋️‍♂️🥗
