# Alembic Database Migration Setup Guide

## ✅ What's Been Set Up

Alembic has been fully configured for your fitness assistant project! Here's what was done:

### 1. **Alembic Initialized**
   - Created `/backend/alembic/` directory with migration infrastructure
   - Created `/backend/alembic.ini` configuration file
   - Created `/backend/alembic/env.py` with proper model imports

### 2. **Migration Created**
   - **Migration File**: `alembic/versions/001_add_fitness_nutrition_fields.py`
   - **Adds 12 New Fitness Columns** to `health_profiles` table:
     - `fitness_level` (beginner/intermediate/advanced)
     - `training_experience` (e.g., "2 years")
     - `fitness_goals` (JSON array)
     - `available_equipment` (JSON array)
     - `training_days_per_week` (integer)
     - `training_duration_minutes` (integer)
     - `current_injuries` (JSON array)
     - `health_conditions` (JSON array)
     - `diet_preference` (string)
     - `dietary_restrictions` (JSON array)
     - `food_allergies` (JSON array)
     - `body_fat_percentage` (float)
     - `body_measurements` (JSON object)
   - **Fixes**: Renames `knowledge_documents.metadata` → `doc_metadata` (reserved keyword fix)

### 3. **Fixed Code Issues**
   - Updated `app/models/database.py` - renamed `metadata` column to `doc_metadata`
   - This prevents SQLAlchemy reserved keyword conflicts

---

## 🚀 How to Run Migrations

### Step 1: Set Up Environment Variables

Create a `.env` file in `/backend/` directory (copy from `.env.example`):

```bash
cp .env.example .env
```

Then edit `.env` with your actual database credentials:

```env
# Minimum required for Alembic:
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fitness_assistant

SECRET_KEY=your-super-secret-key-at-least-32-characters-long
```

### Step 2: Ensure PostgreSQL is Running

Make sure your PostgreSQL database is running and accessible:

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# If not running, start it
sudo systemctl start postgresql
```

### Step 3: Create the Database (if it doesn't exist)

```bash
# Connect to PostgreSQL
psql -U postgres

# Create the database
CREATE DATABASE fitness_assistant;

# Grant privileges to your user
GRANT ALL PRIVILEGES ON DATABASE fitness_assistant TO your_db_user;

# Exit
\q
```

### Step 4: Run the Migration

```bash
# Navigate to backend directory
cd /home/user/doctor_assistant-/backend

# Run the migration
alembic upgrade head
```

You should see output like:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001_fitness_nutrition, Add fitness and nutrition profile fields
```

---

## 📋 Common Alembic Commands

### Check Migration Status
```bash
alembic current
```

### View Migration History
```bash
alembic history --verbose
```

### Upgrade to Latest Version
```bash
alembic upgrade head
```

### Downgrade One Version
```bash
alembic downgrade -1
```

### Generate Auto Migration (for future changes)
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Create Empty Migration (manual)
```bash
alembic revision -m "Description"
```

---

## 🔍 Verifying the Migration

After running `alembic upgrade head`, verify the columns were added:

```bash
# Connect to your database
psql -U your_db_user -d fitness_assistant

# Describe the health_profiles table
\d health_profiles

# You should see all the new fitness columns listed
```

---

## ⚠️ Troubleshooting

### Error: "Module 'pydantic' not found"
```bash
pip install pydantic pydantic-settings python-dotenv
```

### Error: "Module 'psycopg2' not found"
```bash
pip install psycopg2-binary
```

### Error: "Connection refused"
- Ensure PostgreSQL is running: `sudo systemctl start postgresql`
- Check your database credentials in `.env`
- Verify `POSTGRES_HOST` and `POSTGRES_PORT` are correct

### Error: "Database does not exist"
```bash
psql -U postgres -c "CREATE DATABASE fitness_assistant;"
```

---

## 📝 What's in the Migration?

The migration adds support for the complete fitness assistant transformation:

**Fitness Assessment**:
- Tracks user's fitness level and training experience
- Stores fitness goals (muscle gain, fat loss, strength, etc.)

**Training Programs**:
- Equipment availability for workout customization
- Training schedule (days per week, session duration)

**Health & Safety**:
- Current injuries to avoid aggravating
- Health conditions to consider in programming

**Nutrition Planning**:
- Diet preferences (Persian cuisine support!)
- Dietary restrictions (vegetarian, vegan, etc.)
- Food allergies tracking

**Body Composition**:
- Body fat percentage tracking
- Body measurements (chest, waist, hips, arms)

---

## 🎯 Next Steps

After running migrations:

1. **Start the backend server**:
   ```bash
   cd /home/user/doctor_assistant-/backend
   uvicorn app.main:app --reload
   ```

2. **Test the profile form**: The frontend ProfilePage has been updated with all fitness fields

3. **Test the onboarding flow**: The OnboardingAgent will collect fitness information conversationally

---

## 📦 Future Migrations

When you need to add more columns or modify the schema:

1. **Update the SQLAlchemy models** in `app/models/database.py`

2. **Generate migration automatically**:
   ```bash
   alembic revision --autogenerate -m "Your change description"
   ```

3. **Review the generated migration** in `alembic/versions/`

4. **Apply the migration**:
   ```bash
   alembic upgrade head
   ```

---

## ✨ Summary

✅ Alembic is fully configured
✅ Migration created with 12 new fitness fields
✅ Reserved keyword conflict fixed (`metadata` → `doc_metadata`)
✅ Ready to run `alembic upgrade head` once database is set up

Your fitness assistant is ready for database migrations! 🎉
