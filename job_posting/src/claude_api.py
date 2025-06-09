import asyncio
import logging
from typing import Dict, Any, Optional
from anthropic import Anthropic, APIStatusError
from config.settings import ANTHROPIC_API_KEY, DEFAULT_MODEL, SYSTEM_INSTRUCTIONS

logger = logging.getLogger(__name__)

class QuotaExceededError(Exception):
    """Exception raised when the Claude rate limit is exceeded"""
    pass

class ClaudeAPI:
    def __init__(self):
        # Initialize Claude client
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        logger.info("Claude client initialized successfully")
        
        # Configuration for content generation
        self.generation_config: Dict[str, Any] = {
            "max_tokens": 4096,
            "temperature": 0.7,
        }

    async def send_message(self, message: str, context: str = "") -> str:
        """
        Send a user message to Claude with optional context from vector search.
        """
        for attempt in range(3):
            try:
                # Prepare the message with context if available
                if context:
                    full_message = f"""Context from knowledge base:
{context}

User request:
{message}

Please use the context above to generate a response. If this is for LinkedIn platform, use the LinkedIn-specific formatting from the knowledge base.

CRITICAL FORMATTING REQUIREMENTS:
- Each bullet point with emoji (🔹 ✅ 📊 🎯) MUST be on its own separate line
- Add a line break after each bullet point
- Use proper paragraph spacing between sections
- Never put multiple bullet points on the same line
- Ensure readability on LinkedIn platform"""
                else:
                    full_message = f"""{message}

CRITICAL FORMATTING REQUIREMENTS:
- Each bullet point with emoji (🔹 ✅ 📊 🎯) MUST be on its own separate line
- Add a line break after each bullet point
- Use proper paragraph spacing between sections
- Never put multiple bullet points on the same line
- Ensure readability on LinkedIn platform"""
                
                # Call Claude API
                response = await asyncio.to_thread(
                    self.client.messages.create,
                    model=DEFAULT_MODEL,
                    max_tokens=self.generation_config["max_tokens"],
                    temperature=self.generation_config["temperature"],
                    system=SYSTEM_INSTRUCTIONS,
                    messages=[
                        {
                            "role": "user",
                            "content": full_message
                        }
                    ]
                )
                
                return response.content[0].text
                
            except APIStatusError as e:
                if e.status_code == 429:  # Rate limit
                    if attempt < 2:
                        logger.warning(f"Rate limit encountered (attempt {attempt+1}/3): {e}")
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise QuotaExceededError("Claude rate limit exceeded after retries")
                else:
                    logger.error(f"Claude API error: {e}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise
        
        # Final fallback if all retries exhausted
        raise QuotaExceededError("Claude rate limit exceeded after retries")

    async def send_message_stream(self, message: str, context: str = ""):
        """
        Stream a response from Claude with optional context.
        """
        for attempt in range(3):
            try:
                # Prepare the message with context if available
                if context:
                    full_message = f"""Context from knowledge base:
{context}

User request:
{message}

Please use the context above to generate a response. If this is for LinkedIn platform, use the LinkedIn-specific formatting from the knowledge base.

CRITICAL FORMATTING REQUIREMENTS:
- Each bullet point with emoji (🔹 ✅ 📊 🎯) MUST be on its own separate line
- Add a line break after each bullet point
- Use proper paragraph spacing between sections
- Never put multiple bullet points on the same line
- Ensure readability on LinkedIn platform"""
                else:
                    full_message = f"""{message}

CRITICAL FORMATTING REQUIREMENTS:
- Each bullet point with emoji (🔹 ✅ 📊 🎯) MUST be on its own separate line
- Add a line break after each bullet point
- Use proper paragraph spacing between sections
- Never put multiple bullet points on the same line
- Ensure readability on LinkedIn platform"""
                
                # Stream response from Claude
                stream = await asyncio.to_thread(
                    self.client.messages.create,
                    model=DEFAULT_MODEL,
                    max_tokens=self.generation_config["max_tokens"],
                    temperature=self.generation_config["temperature"],
                    system=SYSTEM_INSTRUCTIONS,
                    messages=[
                        {
                            "role": "user",
                            "content": full_message
                        }
                    ],
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.type == "content_block_delta":
                        if hasattr(chunk.delta, 'text'):
                            yield chunk.delta.text
                return
                
            except APIStatusError as e:
                if e.status_code == 429:  # Rate limit
                    logger.warning(f"Stream rate limit encountered (attempt {attempt+1}/3): {e}")
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    logger.error(f"Claude API error: {e}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error in streaming: {e}")
                raise
        
        # Final fallback
        raise QuotaExceededError("Claude rate limit exceeded after retries")