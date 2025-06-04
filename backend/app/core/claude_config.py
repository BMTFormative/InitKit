# backend/app/core/claude_config.py
from typing import Dict, List
from pathlib import Path

# Claude API Configuration
AVAILABLE_CLAUDE_MODELS = {
    "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet (Latest)",
    "claude-3-haiku-20240307": "Claude 3 Haiku (Fast)",
}

DEFAULT_CLAUDE_MODEL = "claude-3-5-sonnet-20241022"

# Knowledge Base Configuration
KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent / "knowledge_base"

# Job Posting Generation Configuration
JOB_POSTING_GENERATION_CONFIG = {
    "max_tokens": 4096,
    "temperature": 0.7,
}

# Platform-specific formatting rules
PLATFORM_FORMATTING = {
    "linkedin": {
        "use_emojis": True,
        "bullet_style": "🔹 ✅ 🚀",
        "max_paragraph_length": 150,
        "hashtags": True,
    },
    "indeed": {
        "use_emojis": False,
        "bullet_style": "•",
        "max_paragraph_length": 200,
        "hashtags": False,
    },
    "glassdoor": {
        "use_emojis": False,
        "bullet_style": "•",
        "max_paragraph_length": 250,
        "hashtags": False,
    },
}

# System instructions for Claude
SYSTEM_INSTRUCTIONS = """You are a specialized job posting assistant. Your role is to create compelling, professional job postings based on the provided information and your knowledge base.

CRITICAL INSTRUCTIONS:
- If the user asks to create a LinkedIn job posting, refer exclusively to the LinkedIn-specific guidelines from your knowledge base
- For other platforms, use the general best practices from your knowledge base
- Produce unique, original job descriptions - never copy content directly
- Use professional language that's inclusive and aligned with company branding

FORMATTING RULES:
- For LinkedIn: Use emojis (🔹 ✅ 🚀), concise bullet points, short paragraphs
- Include clear sections: title, company overview, job summary, responsibilities, qualifications, benefits
- Make content engaging and attractive to potential candidates
- Never include external links in job postings

Always maintain a professional, informative tone while being accurate and detail-oriented."""