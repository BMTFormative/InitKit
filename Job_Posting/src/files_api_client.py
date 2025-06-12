"""
Files API Client for Claude
Uses Claude's Files API with knowledge base document references
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Tuple, List, AsyncGenerator
from anthropic import Anthropic, APIStatusError
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class FilesAPIClient:
    """
    Files API client for Claude with knowledge base integration
    """
    
    def __init__(self):
        # Load configuration
        from config.settings import (
            ANTHROPIC_API_KEY, 
            FILES_API_BETA_VERSION,
            KNOWLEDGE_BASE_FILES,
            MODEL_PRICING
        )
        
        self.api_key = ANTHROPIC_API_KEY
        self.beta_version = FILES_API_BETA_VERSION
        self.file_ids = KNOWLEDGE_BASE_FILES
        self.model_pricing = MODEL_PRICING
        
        # Initialize Files API client
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required")
        
        try:
            self.client = Anthropic(api_key=self.api_key)
            logger.info(f"Files API client initialized with File IDs: {list(self.file_ids.keys())}")
                
        except Exception as e:
            logger.error(f"Failed to initialize client: {e}")
            raise RuntimeError(f"Client initialization failed: {e}")
        
        logger.info("Files API client ready - using knowledge base via File IDs")
    
    
    async def generate_with_token_count(
        self, 
        message: str, 
        platform: str = "linkedin",
        model: str = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate job posting with token counting using Files API"""
        from config.settings import DEFAULT_MODEL
        
        if model is None:
            model = DEFAULT_MODEL
        
        return await self._generate_with_files_api(message, platform, model)
    
    async def generate_streaming(
        self, 
        message: str, 
        platform: str = "linkedin",
        model: str = None
    ) -> AsyncGenerator[str, None]:
        """Generate job posting with streaming response using Files API"""
        from config.settings import DEFAULT_MODEL
        
        if model is None:
            model = DEFAULT_MODEL
        
        async for chunk in self._generate_files_api_streaming(message, platform, model):
            yield chunk
    
    async def _generate_with_files_api(self, message: str, platform: str, model: str) -> Tuple[str, Dict[str, Any]]:
        """Generate using Files API with knowledge base documents"""
        try:
            # Build content blocks with Files API
            content_blocks = [{"type": "text", "text": message}]
            files_used = []
            
            # Add document blocks
            if platform.lower() == "linkedin" and "linkedin_guide" in self.file_ids:
                file_id = self.file_ids["linkedin_guide"]
                content_blocks.append({
                    "type": "document",
                    "source": {
                        "type": "file",
                        "file_id": file_id
                    },
                    "title": "LinkedIn Job Posting Guidelines"
                })
                files_used.append(f"LinkedIn Guide ({file_id})")
                logger.info(f"✅ Adding LinkedIn Guide file: {file_id}")
            
            if "kb2" in self.file_ids:
                file_id = self.file_ids["kb2"]
                content_blocks.append({
                    "type": "document",
                    "source": {
                        "type": "file", 
                        "file_id": file_id
                    },
                    "title": "Additional Job Posting Guidelines"
                })
                files_used.append(f"KB2 Guide ({file_id})")
                logger.info(f"✅ Adding KB2 file: {file_id}")
            
            logger.info(f"🚀 Files API Request - Platform: {platform}, Files: {len(files_used)}")
            logger.info(f"📄 Files being used: {', '.join(files_used)}")
            
            response = await asyncio.to_thread(
                self.client.beta.messages.create,
                model=model,
                max_tokens=8000,
                temperature=0.7,
                system=self._get_system_instructions(),
                messages=[{"role": "user", "content": content_blocks}],
                betas=[self.beta_version]
            )
            
            response_text = response.content[0].text
            
            # Extract token usage
            usage = getattr(response, 'usage', None)
            if usage:
                input_tokens = getattr(usage, 'input_tokens', 0)
                output_tokens = getattr(usage, 'output_tokens', len(response_text) // 4)
            else:
                input_tokens = 0
                output_tokens = len(response_text) // 4
            
            cost_breakdown = self._calculate_cost(model, input_tokens, output_tokens)
            
            usage_stats = {
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost_breakdown": cost_breakdown,
                "files_api_used": True,
                "files_used": files_used,
                "usage_report": self._format_usage_report(model, input_tokens, output_tokens, cost_breakdown)
            }
            
            logger.info(f"✅ Files API generation completed - {len(files_used)} files used")
            
            return response_text, usage_stats
            
        except Exception as e:
            logger.error(f"Files API generation error: {e}")
            raise RuntimeError(f"Files API generation failed: {e}")
    
    async def _generate_files_api_streaming(self, message: str, platform: str, model: str) -> AsyncGenerator[str, None]:
        """Generate using Files API with streaming"""
        try:
            # Build content blocks with Files API
            content_blocks = [{"type": "text", "text": message}]
            files_used = []
            
            # Add document blocks
            if platform.lower() == "linkedin" and "linkedin_guide" in self.file_ids:
                file_id = self.file_ids["linkedin_guide"]
                content_blocks.append({
                    "type": "document",
                    "source": {
                        "type": "file",
                        "file_id": file_id
                    },
                    "title": "LinkedIn Job Posting Guidelines"
                })
                files_used.append(f"LinkedIn Guide ({file_id})")
                logger.info(f"🎬 Streaming - Adding LinkedIn Guide file: {file_id}")
            
            if "kb2" in self.file_ids:
                file_id = self.file_ids["kb2"]
                content_blocks.append({
                    "type": "document",
                    "source": {
                        "type": "file", 
                        "file_id": file_id
                    },
                    "title": "Additional Job Posting Guidelines"
                })
                files_used.append(f"KB2 Guide ({file_id})")
                logger.info(f"🎬 Streaming - Adding KB2 file: {file_id}")
            
            logger.info(f"🚀 Files API Streaming - Platform: {platform}, Files: {len(files_used)}")
            logger.info(f"📄 Streaming with files: {', '.join(files_used)}")
            
            def _create_stream():
                return self.client.beta.messages.stream(
                    model=model,
                    max_tokens=8000,
                    temperature=0.7,
                    system=self._get_system_instructions(),
                    messages=[{"role": "user", "content": content_blocks}],
                    betas=[self.beta_version]
                )
            
            stream = await asyncio.to_thread(_create_stream)
            with stream as s:
                for chunk in s.text_stream:
                    yield chunk
                        
        except Exception as e:
            logger.error(f"Files API streaming error: {e}")
            raise RuntimeError(f"Files API streaming failed: {e}")
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> Dict[str, float]:
        """Calculate cost breakdown"""
        pricing = self.model_pricing.get(model, {"input": 0, "output": 0})
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost
        }
    
    def _format_usage_report(self, model: str, input_tokens: int, output_tokens: int, cost_breakdown: Dict[str, float]) -> str:
        """Format usage report"""
        return f"""Token Usage Report:
Model: {model}
Input tokens: {input_tokens:,}
Output tokens: {output_tokens:,}
Total tokens: {input_tokens + output_tokens:,}
Input cost: ${cost_breakdown['input_cost']:.6f}
Output cost: ${cost_breakdown['output_cost']:.6f}
Total cost: ${cost_breakdown['total_cost']:.6f}"""
    
    def _get_system_instructions(self) -> str:
        """Get system instructions for Claude"""
        return """You are a professional job posting specialist. Create compelling, well-structured job postings based on the provided information and guidelines.

Key Requirements:
- Use clear, engaging language that attracts qualified candidates
- Structure content with proper sections: overview, responsibilities, requirements, benefits
- For LinkedIn: Use emojis (🔹 ✅ 🚀), short paragraphs, social media optimization
- Ensure inclusive language and avoid bias
- Include all provided details in an organized manner
- Create unique, original content that stands out

CRITICAL FORMATTING REQUIREMENTS:
- Use proper Markdown formatting with clear line breaks
- Each bullet point must be on a new line with proper spacing
- Use "• " for bullet points with space after the bullet
- Separate sections with double line breaks
- Use ## for main headers, ### for subsections
- Ensure paragraphs are separated with blank lines

Example format:
## Job Title

Brief overview paragraph.

## Key Responsibilities

• Responsibility 1
• Responsibility 2
• Responsibility 3

## Requirements

• Requirement 1
• Requirement 2

Always maintain a professional tone while being engaging and informative."""
    
    async def analyze_tokens(self, message: str, model: str) -> Dict[str, Any]:
        """Analyze token usage for a message"""
        try:
            estimated_tokens = len(message) // 4
            cost_breakdown = self._calculate_cost(model, estimated_tokens, 0)
            
            return {
                "model": model,
                "estimated_input_tokens": estimated_tokens,
                "estimated_input_cost": cost_breakdown["input_cost"],
                "files_api_used": True,
                "method": "files_api"
            }
            
        except Exception as e:
            logger.error(f"Token analysis error: {e}")
            return {"error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get client status"""
        return {
            "files_api_used": True,
            "mode": "Files API",
            "file_ids": self.file_ids,
            "knowledge_base_files": len(self.file_ids),
            "status": "ready"
        }