import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Claude API Configuration - Required for Files API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    import warnings
    warnings.warn("ANTHROPIC_API_KEY not found - Files API will not work", UserWarning)

# Available models for generation
AVAILABLE_MODELS = {
    "claude-opus-4-20250514": "Claude Opus 4 (2025-05-14)",
    "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
    "claude-3-haiku-20240307": "Claude 3 Haiku"
}

# Model pricing per 1M tokens (in USD)
MODEL_PRICING = {
    "claude-opus-4-20250514": {
        "input": 15.00,  # $15 per 1M input tokens
        "output": 75.00  # $75 per 1M output tokens
    },
    "claude-3-5-sonnet-20241022": {
        "input": 3.00,   # $3 per 1M input tokens
        "output": 15.00  # $15 per 1M output tokens
    },
    "claude-3-haiku-20240307": {
        "input": 0.25,   # $0.25 per 1M input tokens
        "output": 1.25   # $1.25 per 1M output tokens
    }
}

# Default model if none specified
DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-20250514")

# Files API Configuration
FILES_API_ENABLED = True
FILES_API_BETA_VERSION = "files-api-2025-04-14"

# Knowledge Base Files Configuration
# Files API File IDs for the knowledge base documents
KNOWLEDGE_BASE_FILES = {
    "linkedin_guide": "file_011CPyPcGRoAaFvfgesUGUHM",
    "kb2": "file_011CPyPcKPtwMaPZfnCdPvdq"
}

# System instructions for job posting generation
SYSTEM_INSTRUCTIONS = """You are a specialized job posting assistant using Claude's Files API. Your role is to create compelling, professional job postings based on the provided information and the attached knowledge base documents.

CRITICAL INSTRUCTIONS:
- You have access to job posting guidelines through Files API documents
- For LinkedIn job postings, refer to the "Crafting Compelling LinkedIn Job Posts" document
- Use the additional knowledge base document for general best practices and other platforms
- Produce unique, original job descriptions - never copy content directly
- Use professional language that's inclusive and aligned with company branding
- Leverage the Files API documents to ensure consistent quality and formatting

FORMATTING RULES:
- For LinkedIn: Use emojis (🔹 ✅ 🚀), concise bullet points, short paragraphs
- For other platforms: Use structured, professional formatting
- Include clear sections: title, company overview, job summary, responsibilities, qualifications, benefits
- Make content engaging and attractive to potential candidates
- Never include external links in job postings

FILES API INTEGRATION:
- Knowledge base content is provided via Files API for optimal token efficiency
- Documents are automatically included in your context for each request
- Use the document content to inform your responses while maintaining originality

Always maintain a professional, informative tone while being accurate and detail-oriented."""

# Token counting settings
TOKEN_COUNTING_ENABLED = True
COST_TRACKING_ENABLED = True