# 🏗️ IRIS Job Posting Generator - Architecture and Structure

## 📋 Overview
FastAPI web application using Claude's Files API to generate professional, AI-optimized job postings.

## 🗂️ File Structure

### 📁 **ESSENTIAL FILES (TO KEEP)**

#### **🔧 Configuration**
- **`.env`** - Environment variables (Anthropic API key)
- **`requirements.txt`** - Essential Python dependencies
- **`config/__init__.py`** - Configuration module
- **`config/settings.py`** - Centralized configuration (API keys, models, pricing)

#### **🚀 Main Application**
- **`main.py`** - FastAPI entry point, defines all API endpoints
- **`src/__init__.py`** - Main source module
- **`src/files_api_client.py`** - Claude Files API client (application core)

#### **🎨 User Interface**
- **`templates/index.html`** - Complete web interface (IRIS Job Posting Generator)
- **`static/scripts.js`** - JavaScript for interactivity (accordion, generation, themes)
- **`static/styles.css`** - Custom CSS styles

#### **📚 Knowledge Base**
- **`data/knowledge_base/Crafting Compelling LinkedIn Job Posts.txt`** - LinkedIn guide
- **`data/knowledge_base/KB2.txt`** - Additional guidelines
- **`data/user_prefs.json`** - User preferences

---

### 🗑️ **FILES TO DELETE**

#### **📁 Complete old project**
- **`Job_Posting_Claude/`** - Old RAG/Vector Store version (ENTIRE FOLDER)

#### **🧪 Temporary test scripts**
- **`test_files_api.py`** - Basic Files API test
- **`test_files_api_only.py`** - Exclusive mode test
- **`test_files_verification.py`** - Verification test
- **`ui_comparison_test.py`** - UI comparison test
- **`quick_test.py`** - Quick test
- **`final_test.py`** - Final test

#### **🔄 Alternative launch scripts**
- **`run.py`** - Simple launch script
- **`run_with_env.py`** - Script with env variables
- **`start.py`** - Alternative startup script

#### **📚 Temporary documentation**
- **`FILES_API_ONLY_MODE.md`** - Temporary documentation
- **`DEPLOYMENT_INSTRUCTIONS.md`** - Obsolete instructions
- **`README_FILES_API.md`** - Temporary README

#### **🔧 Development files**
- **`src/files_api_client_strict.py`** - Temporary strict version
- **`.claude/settings.local.json`** - Local Claude settings

#### **📦 Basic deployment scripts**
- **`deploy.bat`** - Basic Windows deployment script
- **`deploy.sh`** - Basic Unix deployment script

---

## 📖 **ROLE OF EACH ESSENTIAL FILE**

### **🔧 Configuration and Infrastructure**

**`main.py`**
- FastAPI entry point
- Defines all API endpoints (/api/generate/job-posting, /api/settings, etc.)
- Handles response streaming
- Interface between web and Claude API

**`config/settings.py`**
- Centralized configuration (API key, Claude models)
- File IDs for Files API (linkedin_guide, kb2)
- Model pricing for cost calculation
- Environment variables and security

**`.env`**
- ANTHROPIC_API_KEY (essential for Claude API)
- CLAUDE_MODEL (default model)

**`requirements.txt`**
- fastapi>=0.100.0 (web framework)
- uvicorn[standard]>=0.20.0 (ASGI server)
- anthropic>=0.30.0 (Claude SDK)
- python-dotenv>=1.0.0 (env variables)
- pydantic>=2.0.0 (data validation)

### **🤖 Artificial Intelligence**

**`src/files_api_client.py`**
- **APPLICATION CORE** : Claude Files API client
- File ID management for knowledge base
- Real-time response streaming
- Compatible mode (fallback with system instructions)
- Token and cost calculation
- Interface between FastAPI and Claude API

### **🎨 User Interface**

**`templates/index.html`**
- Complete "IRIS Job Posting Generator" interface
- 5-step accordion form
- Theme management (light/dark)
- Export buttons (Markdown, DOCX, PDF, Google Docs)
- Sections: Essential Info, Job Context, Qualifications, Benefits, Publication
- Smart tips for complete content vs form

**`static/scripts.js`**
- Complete JavaScript logic
- Accordion and progress management
- API communication (fetch, streaming)
- Themes and localStorage
- Smart content analysis
- Multi-format export
- Error handling and notifications

**`static/styles.css`**
- Custom CSS styles
- Theme variables (--surface, etc.)
- Animations and transitions
- Responsive design
- Loaders and indicators

### **📚 Knowledge Base**

**`data/knowledge_base/Crafting Compelling LinkedIn Job Posts.txt`**
- Specialized LinkedIn guide (File ID: file_011CPyPcGRoAaFvfgesUGUHM)
- LinkedIn-specific best practices
- Used automatically for platform="linkedin"

**`data/knowledge_base/KB2.txt`**
- General guidelines (File ID: file_011CPyPcKPtwMaPZfnCdPvdq)
- Multi-platform best practices
- Used for all generations

**`data/user_prefs.json`**
- User preferences (company name, etc.)
- Persists settings between sessions

---

## 🏗️ **TECHNICAL ARCHITECTURE**

### **Data Flow:**
1. **User** → HTML interface (accordion, form)
2. **JavaScript** → Data collection + API fetch
3. **FastAPI** → Validates and processes request
4. **Files API Client** → Calls Claude with file IDs
5. **Claude API** → Generates with knowledge base
6. **Streaming** → Returns content in real-time
7. **Frontend** → Displays with Markdown formatting

### **Integrations:**
- **Claude Files API** : Knowledge base via file IDs
- **FastAPI** : Modern, performant web backend
- **Streaming** : Real-time responses
- **Multi-export** : Markdown, DOCX, PDF, Google Docs
- **Responsive** : Adaptive mobile/desktop interface

### **Security:**
- API key in environment variable
- Pydantic input validation
- CORS configured
- No sensitive data storage

---

## 🎯 **READY FOR GITHUB**

After removing unnecessary files, the architecture will be:
```
iris-job-posting-generator/
├── main.py
├── requirements.txt
├── .env
├── config/
│   ├── __init__.py
│   └── settings.py
├── src/
│   ├── __init__.py
│   └── files_api_client.py
├── templates/
│   └── index.html
├── static/
│   ├── scripts.js
│   └── styles.css
├── data/
│   ├── knowledge_base/
│   │   ├── Crafting Compelling LinkedIn Job Posts.txt
│   │   └── KB2.txt
│   └── user_prefs.json
└── README.md
```

**Application ready for production with clean and modular architecture! 🚀**