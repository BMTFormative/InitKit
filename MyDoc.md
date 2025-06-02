# Project Setup and Development Guide

## 📚 How to Use This Documentation

This project has a comprehensive documentation system in the `Documentation/` folder to help with development:

### 📖 Documentation Files Overview
- **📋 PROJECT UNDERSTANDING SUMMARY** - Start here for complete platform overview
- **📖 Application Overview** - Business model and core features explanation
- **📊 Database Models Map** - Data structure and relationships
- **🔌 API Structure Guide** - Backend API organization and flows
- **📁 File Reference Guide** - Where to make specific changes (Frontend + Backend)
- **🛠️ This Setup Guide** - Installation and development workflow

### 🎯 Quick Navigation Guide
- **New to the project?** → Start with "PROJECT UNDERSTANDING SUMMARY"
- **Need to add a feature?** → Check "File Reference Guide" for exact file locations
- **Database changes?** → Use "Database Models Map" for structure understanding
- **API modifications?** → Reference "API Structure Guide" for patterns
- **Business logic questions?** → See "Application Overview" for context

### 💡 Development Workflow
1. **Understand the change** → Use relevant documentation files
2. **Locate files** → Check "File Reference Guide"
3. **Follow patterns** → Reference existing code structure
4. **Test changes** → Use commands in this setup guide
5. **Update docs** → Keep documentation current

---

## 🚀 Development Environment Setup

### 📋 Prerequisites
- **Git for Windows** (https://git-scm.com/)
- **Python 3.10+** with python & pip on PATH
- **Node.js 16+** (includes npm)
- **PostgreSQL** installed locally
- **VS Code** (recommended) with Python and TypeScript extensions

### 🗄️ Database Setup
1. **Install PostgreSQL locally**
2. **Create a database** (e.g., `fastapi_template_db`)
3. **Note your credentials** (username, password, database name)

---

## 📁 Project Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/tiangolo/full-stack-fastapi-postgresql.git
# Rename the project folder
move full-stack-fastapi-postgresql my-project
cd my-project
```

### 2️⃣ Backend Setup (FastAPI + Python)

#### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# If you get execution policy error:
# Get-ExecutionPolicy
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Upgrade pip
python.exe -m pip install --upgrade pip

# Install dependencies
uv sync
```

#### Database Configuration
Create/edit `.env` file in project root:
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=your_pg_user
POSTGRES_PASSWORD=your_pg_password
POSTGRES_DB=fastapi_template_db
SECRET_KEY=changethis
FIRST_SUPERUSER_PASSWORD=changethis
```

#### Database Migration
```bash
cd backend
# Initialize database with latest migrations
alembic upgrade head

# Create first superuser (optional)
python -m app.initial_data
```

### 3️⃣ Frontend Setup (React + TypeScript)

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Environment Configuration
Create `.env.development` in frontend folder:
```env
VITE_API_URL=http://localhost:8000
```

---

## 🏃‍♂️ Running the Application

### 🔧 Backend (FastAPI)
```bash
# Navigate to backend and activate venv
cd backend
.venv\Scripts\Activate.ps1

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API will be available at:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### 🎨 Frontend (React)
```bash
# Navigate to frontend
cd frontend

# Start development server
npm run dev

# Frontend will be available at:
# http://localhost:3000 (or port shown in terminal)
```

---

## 🔧 Development Commands

### Backend Commands
```bash
# Run tests
bash backend/scripts/test.sh

# Format code
bash backend/scripts/format.sh

# Lint code
bash backend/scripts/lint.sh

# Create new migration
cd backend
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Frontend Commands
```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

---

## 🗄️ Database Management

### Reset Database (if needed)
```bash
# For PostgreSQL - DROP and recreate schema
psql -U your_username -d your_database_name -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Remove migration files (keep __init__.py)
rm backend/app/alembic/versions/*.py

# Create fresh migration
cd backend
alembic revision --autogenerate -m "initial_migration"

# Apply migration
alembic upgrade head
```

### Add Subscription Models (if updating)
```bash
cd backend
alembic revision --autogenerate -m "add subscription models"
alembic upgrade head
```

---

## 📦 Git Repository Setup

### Initialize Your Own Repository
```bash
# Create empty repo on GitHub (e.g., my-fastapi-template)

# In your project root, remove origin and add yours:
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YourUsername/YourRepo.git
git push -u origin main
```

---

## 🚨 Troubleshooting

### Common Issues

#### Migration Problems
If you encounter migration issues:
```bash
# Reset migrations completely
rm backend/app/alembic/versions/*.py
cd backend
alembic revision --autogenerate -m "initial_setup"
alembic upgrade head
```

#### PowerShell Execution Policy
If you can't activate the virtual environment:
```powershell
Get-ExecutionPolicy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Database Connection Issues
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists
- Test connection: `psql -U username -d database_name`

#### Frontend API Connection
- Verify backend is running on port 8000
- Check `VITE_API_URL` in frontend `.env.development`
- Check browser console for CORS errors

### Environment Variables
Always update these before deployment:
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `FIRST_SUPERUSER_PASSWORD` - Set a secure password
- `POSTGRES_PASSWORD` - Use a strong database password

---

## 🎯 Next Steps

1. **Review Documentation** → Check `Documentation/` folder for project understanding
2. **Explore the Code** → Start with `backend/app/models.py` and `frontend/src/components/`
3. **Run Tests** → Ensure everything works: `bash backend/scripts/test.sh`
4. **Make Changes** → Use the "File Reference Guide" to know where to modify files
5. **Stay Updated** → Keep documentation current as you add features

## 📞 Need Help?

- **Backend Issues** → Check FastAPI docs and `backend/app/` structure
- **Frontend Issues** → Review React/Chakra UI docs and `frontend/src/` organization
- **Database Issues** → Check PostgreSQL logs and migration files
- **Architecture Questions** → Reference the documentation files in `Documentation/` folder

Happy coding! 🚀