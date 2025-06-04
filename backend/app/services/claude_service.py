# backend/app/services/claude_service.py
import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import re

from anthropic import Anthropic, APIStatusError
from sqlmodel import Session

from app.core.claude_config import (
    DEFAULT_CLAUDE_MODEL,
    JOB_POSTING_GENERATION_CONFIG,
    SYSTEM_INSTRUCTIONS,
    KNOWLEDGE_BASE_PATH,
    PLATFORM_FORMATTING,
)
from app.services.credit_service import CreditService

logger = logging.getLogger(__name__)


class QuotaExceededError(Exception):
    """Exception raised when the Claude rate limit is exceeded"""
    pass


class KnowledgeBaseManager:
    """Manages loading and searching knowledge base content"""
    
    def __init__(self):
        self.knowledge_base = {}
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Load knowledge base files"""
        try:
            kb_path = Path(KNOWLEDGE_BASE_PATH)
            
            # Load LinkedIn guidelines
            linkedin_file = kb_path / "linkedin_guidelines.txt"
            if linkedin_file.exists():
                with open(linkedin_file, 'r', encoding='utf-8') as f:
                    self.knowledge_base['linkedin'] = f.read()
            
            # Load general best practices
            general_file = kb_path / "general_best_practices.txt"
            if general_file.exists():
                with open(general_file, 'r', encoding='utf-8') as f:
                    self.knowledge_base['general'] = f.read()
                    
            logger.info(f"Loaded knowledge base with {len(self.knowledge_base)} sources")
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            self.knowledge_base = {}
    
    def get_context(self, platform: str = None, query: str = "") -> str:
        """Get relevant context from knowledge base"""
        context_parts = []
        
        # Add platform-specific context
        if platform and platform.lower() == 'linkedin' and 'linkedin' in self.knowledge_base:
            context_parts.append("LinkedIn Job Posting Guidelines:")
            context_parts.append(self.knowledge_base['linkedin'][:2000])  # Limit size
        
        # Add general best practices
        if 'general' in self.knowledge_base:
            context_parts.append("General Job Posting Best Practices:")
            context_parts.append(self.knowledge_base['general'][:2000])  # Limit size
        
        return "\n\n---\n\n".join(context_parts)


class ClaudeService:
    """Service for integrating with Claude AI for job posting generation"""
    
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.kb_manager = KnowledgeBaseManager()
        logger.info("Claude service initialized successfully")
    
    async def generate_job_posting(
        self,
        job_data: Dict[str, Any],
        model: str = DEFAULT_CLAUDE_MODEL
    ) -> Dict[str, Any]:
        """Generate a job posting using Claude AI"""
        
        try:
            # Build the prompt
            prompt = self._build_job_posting_prompt(job_data)
            
            # Get knowledge base context
            platform = job_data.get('platform', '')
            context = self.kb_manager.get_context(platform, job_data.get('job_title', ''))
            
            # Prepare the full message
            full_message = self._prepare_message(prompt, context, platform)
            
            # Call Claude API
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=model,
                max_tokens=JOB_POSTING_GENERATION_CONFIG["max_tokens"],
                temperature=JOB_POSTING_GENERATION_CONFIG["temperature"],
                system=SYSTEM_INSTRUCTIONS,
                messages=[
                    {
                        "role": "user",
                        "content": full_message
                    }
                ]
            )
            
            content = response.content[0].text
            
            # Format the content based on platform
            formatted_content = self._format_content(content, platform)
            
            return {
                "content": formatted_content,
                "model_used": model,
                "knowledge_sources": list(self.kb_manager.knowledge_base.keys()),
                "success": True
            }
            
        except APIStatusError as e:
            if e.status_code == 429:
                raise QuotaExceededError("Claude rate limit exceeded")
            else:
                logger.error(f"Claude API error: {e}")
                raise
        except Exception as e:
            logger.error(f"Error generating job posting: {e}")
            raise
    
    async def analyze_job_posting(self, content: str) -> Dict[str, Any]:
        """Analyze job posting quality and provide suggestions"""
        
        prompt = f"""
        You are a job posting quality analyzer. Analyze the following job posting and provide:
        1. A quality score from 1-100
        2. A list of specific improvement suggestions
        
        Respond with JSON only in this format:
        {{"score": <int>, "suggestions": [<strings>]}}
        
        Job posting to analyze:
        {content}
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=DEFAULT_CLAUDE_MODEL,
                max_tokens=1000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            text = response.content[0].text.strip()
            
            # Extract JSON
            import json
            if not text.startswith('{'):
                match = re.search(r'\{.*\}', text, re.S)
                if match:
                    text = match.group(0)
            
            data = json.loads(text)
            return {
                "score": int(data.get("score", 0)),
                "suggestions": data.get("suggestions", []),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error analyzing job posting: {e}")
            return {
                "score": 0,
                "suggestions": ["Unable to analyze posting due to technical error"],
                "success": False
            }
    
    def _build_job_posting_prompt(self, job_data: Dict[str, Any]) -> str:
        """Build the prompt for job posting generation"""
        prompt_parts = ["Generate a professional job posting with the following details:"]
        
        # Basic information
        if job_data.get("job_title"):
            prompt_parts.append(f"Position: {job_data['job_title']}")
        
        if job_data.get("location"):
            prompt_parts.append(f"Location: {job_data['location']}")
            
        if job_data.get("experience_level"):
            prompt_parts.append(f"Experience Level: {job_data['experience_level']}")
            
        if job_data.get("employment_type"):
            prompt_parts.append(f"Employment Type: {job_data['employment_type']}")
        
        # Job details
        if job_data.get("job_overview"):
            prompt_parts.append(f"Job Overview: {job_data['job_overview']}")
        
        if job_data.get("responsibilities"):
            resp_text = '\n'.join(f"- {item}" for item in job_data['responsibilities'])
            prompt_parts.append(f"Responsibilities:\n{resp_text}")
        
        if job_data.get("required_skills"):
            prompt_parts.append(f"Required Skills: {job_data['required_skills']}")
        
        if job_data.get("education_requirements"):
            prompt_parts.append(f"Education Requirements: {job_data['education_requirements']}")
        
        # Benefits and compensation
        if job_data.get("include_salary") and job_data.get("salary_range"):
            prompt_parts.append(f"Salary Range: {job_data['salary_range']}")
        
        if job_data.get("benefits"):
            prompt_parts.append(f"Benefits: {', '.join(job_data['benefits'])}")
        
        # Platform and formatting
        if job_data.get("platform"):
            prompt_parts.append(f"Platform: {job_data['platform']}")
        
        if job_data.get("length"):
            prompt_parts.append(f"Length: {job_data['length']}")
        
        return "\n\n".join(prompt_parts)
    
    def _prepare_message(self, prompt: str, context: str, platform: str) -> str:
        """Prepare the full message with context and formatting instructions"""
        message_parts = []
        
        if context:
            message_parts.append(f"Context from knowledge base:\n{context}")
        
        message_parts.append(f"User request:\n{prompt}")
        
        # Add platform-specific formatting instructions
        if platform.lower() in PLATFORM_FORMATTING:
            formatting = PLATFORM_FORMATTING[platform.lower()]
            instructions = []
            
            if formatting.get("use_emojis"):
                instructions.append(f"Use emojis like {formatting['bullet_style']} for bullet points")
            
            instructions.append(f"Use '{formatting['bullet_style']}' for bullet points")
            instructions.append(f"Keep paragraphs under {formatting['max_paragraph_length']} characters")
            
            if formatting.get("hashtags"):
                instructions.append("Include relevant hashtags at the end")
            
            message_parts.append(f"Platform-specific formatting:\n" + "\n".join(instructions))
        
        # Critical formatting requirements
        message_parts.append("""
CRITICAL FORMATTING REQUIREMENTS:
- Each bullet point with emoji MUST be on its own separate line
- Add a line break after each bullet point
- Use proper paragraph spacing between sections
- Never put multiple bullet points on the same line
- Ensure readability on the target platform
        """)
        
        return "\n\n".join(message_parts)
    
    def _format_content(self, content: str, platform: str) -> str:
        """Apply platform-specific formatting to the generated content"""
        
        if platform.lower() == 'linkedin':
            # Fix LinkedIn bullet point formatting
            content = self._fix_linkedin_formatting(content)
        
        return content
    
    def _fix_linkedin_formatting(self, text: str) -> str:
        """Fix LinkedIn bullet point formatting"""
        lines = text.split('\n')
        formatted_lines = []
        
        bullet_emojis = ['🔹', '✅', '📊', '🎯', '💰', '🚀', '🌍', '📋']
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append('')
                continue
            
            # Check if line contains multiple bullet points
            bullet_count = sum(line.count(emoji) for emoji in bullet_emojis)
            
            if bullet_count > 1:
                # Split multiple bullets into separate lines
                for emoji in bullet_emojis:
                    if emoji in line:
                        parts = line.split(emoji)
                        if len(parts) > 1:
                            for i, part in enumerate(parts[1:], 1):  # Skip first empty part
                                if part.strip():
                                    formatted_lines.append(f"{emoji} {part.strip()}")
                        break
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)