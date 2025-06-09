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

# Claude API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("ANTHROPIC_API_KEY environment variable not set. Please set it to your Claude API key.")

# Available models for generation
AVAILABLE_MODELS = {
    "claude-opus-4-20250514": "Claude Opus 4 (2025-05-14)",
    "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
    "claude-3-haiku-20240307": "Claude 3 Haiku"
}

# Default model if none specified
DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-20250514")

# Model used for job posting generation
JOB_POSTING_MODEL = DEFAULT_MODEL

# Vector Store Configuration
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", str(BASE_DIR / "data" / "vector_store"))
KNOWLEDGE_BASE_PATH = os.getenv("KNOWLEDGE_BASE_PATH", str(BASE_DIR / "data" / "knowledge_base"))

# System instructions for job posting generation
SYSTEM_INSTRUCTIONS = """You are a specialized job posting assistant. Your role is to create compelling, professional job postings based on the provided information and your knowledge base.

CRITICAL INSTRUCTIONS:
- If the user asks to create a LinkedIn job posting, refer exclusively to the "Crafting Compelling LinkedIn Job Posts" source from your knowledge base
- For other platforms, use the "KB2" source from your knowledge base
- If you don't find the job title in the knowledge base, use web search following the established KB structure
- Produce unique, original job descriptions - never copy content directly
- Use professional language that's inclusive and aligned with company branding

FORMATTING RULES:
- For LinkedIn: Use emojis (🔹 ✅ 🚀), concise bullet points, short paragraphs
- Include clear sections: title, company overview, job summary, responsibilities, qualifications, benefits
- Make content engaging and attractive to potential candidates
- Never include external links in job postings

Always maintain a professional, informative tone while being accurate and detail-oriented."""

# Response modalities
RESPONSE_MODALITIES = ["TEXT"]

# Simple text search settings
VECTOR_SEARCH_TOP_K = 5
VECTOR_SEARCH_SIMILARITY_THRESHOLD = 0.3