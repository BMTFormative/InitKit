# 🤖 IRIS Job Posting Generator

> **Artificial Intelligence for creating professional optimized job postings**

## 🎯 Overview

IRIS Job Posting Generator is a modern web application that uses Claude's Files API (Anthropic) to create professional, optimized job postings personalized according to the best practices of each platform.

### ✨ Key Features

- 🧠 **Integrated AI** : Uses Claude with specialized knowledge base
- 📋 **Intuitive Interface** : Progressive 5-step form
- 🎨 **Multi-platform** : LinkedIn, Indeed, Glassdoor optimization
- 📱 **Responsive** : Adaptive desktop/mobile interface
- 🌙 **Themes** : Light/dark mode with persistence
- 📄 **Multi-format Export** : Markdown, DOCX, PDF, Google Docs
- ⚡ **Real-time Streaming** : Progressive content generation
- 🎯 **Smart Tips** : Intelligent guidance based on content

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Anthropic API Key (Claude)
- Access to Claude Files API

### Quick Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd iris-job-posting-generator
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configuration**
```bash
# Create .env file
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
echo "CLAUDE_MODEL=claude-opus-4-20250514" >> .env
```

4. **Run the application**
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

5. **Access the interface**
Open http://127.0.0.1:8000 in your browser

## 🏗️ Architecture

### Project Structure
```
iris-job-posting-generator/
├── main.py                    # FastAPI entry point
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── config/
│   ├── __init__.py
│   └── settings.py           # Centralized configuration
├── src/
│   ├── __init__.py
│   └── files_api_client.py   # Claude Files API client
├── templates/
│   └── index.html            # User interface
├── static/
│   ├── scripts.js            # Frontend JavaScript
│   └── styles.css            # CSS styles
├── data/
│   ├── knowledge_base/
│   │   ├── Crafting Compelling LinkedIn Job Posts.txt
│   │   └── KB2.txt           # Additional guidelines
│   └── user_prefs.json       # User preferences
└── README.md
```

### Technologies Used

- **Backend** : FastAPI, Python 3.8+
- **AI** : Claude API (Anthropic) with Files API
- **Frontend** : HTML5, JavaScript ES6+, CSS3
- **Styling** : Tailwind CSS, Custom CSS
- **Export** : jsPDF, docx.js, FileSaver.js
- **Markdown** : marked.js
- **Syntax** : highlight.js

## 📚 Usage

### 5-Step Interface

1. **📝 Essential Information**
   - Job title (required)
   - Job description/overview
   - Smart tip for complete content

2. **🏢 Job Context**
   - Location
   - Experience level
   - Employment type

3. **🎯 Qualifications & Skills**
   - Key responsibilities
   - Required skills
   - Education and certifications

4. **💰 Compensation & Benefits**
   - Salary range (optional)
   - Benefits package
   - Additional perks

5. **🚀 Publication Settings**
   - Target platform
   - Content length
   - Application deadline

### Usage Modes

**🎯 Enhancement Mode (Scenario A)**
- Paste a complete job description
- AI optimizes according to best practices
- Minimal form filling required

**📝 Creation Mode (Scenario B/C)**
- Fill out the form step by step
- AI generates complete content
- Integrated intelligent guidance

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Optional
CLAUDE_MODEL=claude-opus-4-20250514
```

### File IDs (Files API)
Knowledge base documents are referenced by their File IDs:
- **LinkedIn Guide** : `file_011CPyPcGRoAaFvfgesUGUHM`
- **KB2 (Guidelines)** : `file_011CPyPcKPtwMaPZfnCdPvdq`

## 🔧 API Endpoints

- `GET /` - User interface
- `POST /api/generate/job-posting` - Job posting generation (streaming)
- `GET /api/settings` - Retrieve preferences
- `POST /api/settings` - Save preferences
- `POST /api/analyze/job-posting` - Quality analysis
- `POST /api/generate/apply-suggestions` - Apply suggestions
- `POST /api/verify/files-usage` - Files API verification

## 🌟 Advanced Features

### Smart Content Analysis
- Automatic detection of complete vs partial content
- Contextual suggestions
- Adaptive guidance based on mode

### Multi-format Export
- **Markdown** : Native format with syntax
- **DOCX** : Word-compatible document
- **PDF** : High-quality export
- **Google Docs** : Direct opening with content

### Themes and Customization
- Automatic light/dark mode
- Preference persistence
- Responsive interface

## 🔐 Security

- API key stored in environment variable
- Input validation with Pydantic
- CORS configured for web security
- No sensitive data storage

## 📝 Development

### Development Mode Launch
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Modular Structure
- **Centralized Configuration** : `config/settings.py`
- **Isolated AI Client** : `src/files_api_client.py`
- **Decoupled Interface** : Separate templates and static files
- **Robust Validation** : Pydantic models

### Logging and Debugging
The application generates detailed logs for:
- Files API usage
- Token statistics
- Errors and performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is developed by **INOVAITE LTD**.
Copyright © 2025 INOVAITE LTD. All rights reserved.

## 🆘 Support

For any questions or issues:
- Create an issue on GitHub
- Check documentation in `PROJECT_ARCHITECTURE.md`
- Review application logs

---

**Créé avec ❤️ par INOVAITE LTD - Transforming ideas into intelligent solutions**