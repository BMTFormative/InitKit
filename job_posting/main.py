from fastapi import FastAPI, HTTPException, Request
import json
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from pydantic import BaseModel
from pathlib import Path
import logging
import traceback

# Enhanced logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_DIR = BASE_DIR / "data"

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

# Import local modules
from src.chat_manager import ChatManager
from src.claude_api import ClaudeAPI, QuotaExceededError
from src.knowledge_base import KnowledgeBaseManager
from src.text_formatter import TextFormatter
from src.intelligent_enhancement import IntelligentJobEnhancer
import re
from pydantic import BaseModel
from config.settings import AVAILABLE_MODELS, DEFAULT_MODEL, JOB_POSTING_MODEL

# Create FastAPI application
app = FastAPI(
    title="Job Posting Generator - Claude Edition",
    description="Job posting generation interface using Claude AI with custom RAG",
    version="1.0.0"
)

# Middleware for handling exceptions
@app.middleware("http")
async def exception_handling(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal error: {str(e)}"}
        )

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files configuration
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Initialize handlers
chat_manager = ChatManager()
claude_api = ClaudeAPI()
kb_manager = KnowledgeBaseManager()
intelligent_enhancer = IntelligentJobEnhancer(kb_manager)

# Data models
class MessageRequest(BaseModel):
    message: str
    selected_model: str | None = None

    class Config:
        json_schema_extra = {
        "example": {
                "message": "Hello!",
                "selected_model": "claude-opus-4-20250514"
            }
        }

class CreateChatRequest(BaseModel):
    name: str

class RenameChatRequest(BaseModel):
    name: str

class JobPostingRequest(BaseModel):
    job_title: str
    job_description: str | None = None  # For pasted complete job descriptions
    company_name: str | None = None
    location: str | None = None
    experience_level: str | None = None
    employment_type: str | None = None
    job_overview: str | None = None
    responsibilities: list[str] | None = None
    team_intro: str | None = None
    required_skills: str | None = None
    education_requirements: str | None = None
    experience_details: str | None = None
    certifications: str | None = None
    include_salary: bool = False
    salary_range: str | None = None
    benefits: list[str] | None = None
    perks: str | None = None
    platform: str | None = None
    length: str = "standard"
    application_deadline: int | None = None
    application_deadline_date: date | None = None
    keywords: str | None = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_title": "Machine Learning Engineer",
                "platform": "LinkedIn",
                "length": "standard"
            }
    }

# Models for applying suggestions
class ApplySuggestionsRequest(BaseModel):
    original_posting: str
    suggestions: list[str]
    suggestion_comment: str | None = None

# Streaming endpoint to apply suggestions to an existing job posting
@app.post("/api/generate/apply-suggestions")
async def apply_suggestions(request: ApplySuggestionsRequest):
    """Streams an improved job posting by applying user suggestions"""
    if not request.original_posting:
        raise HTTPException(status_code=400, detail="Original posting is required")
    
    parts = []
    parts.append(f"Original Job Posting:\n{request.original_posting}")
    parts.append("Please apply the following suggestions to improve this posting:")
    for s in request.suggestions:
        parts.append(f"- {s}")
    if request.suggestion_comment:
        parts.append(f"Additional instructions: {request.suggestion_comment}")
    parts.append("Return the complete, improved job posting with clear sections.")
    message = "\n".join(parts)

    # Search knowledge base for relevant context
    context = kb_manager.search_knowledge_base(message)

    async def event_stream():
        try:
            async for chunk in claude_api.send_message_stream(message, context):
                yield chunk
        except QuotaExceededError as e:
            yield f"\n[Error: {e}]"
        except Exception as e:
            yield f"\n[Error: {e}]"

    return StreamingResponse(event_stream(), media_type="text/plain")

# Endpoint to analyze a generated job posting and provide quality score and suggestions
class AnalyzeRequest(BaseModel):
    posting: str
    selected_model: str | None = None

class AnalyzeResponse(BaseModel):
    score: int
    suggestions: list[str]

@app.post("/api/analyze/job-posting", response_model=AnalyzeResponse)
async def analyze_job_posting(req: AnalyzeRequest):
    """Analyze the given job posting and return a quality score and suggestions"""
    
    # Prompt for analysis: JSON-only response required
    prompt = (
        "You are a JSON-only analysis tool. "
        "Respond with a JSON object only, formatted exactly as: {\"score\": <int>, \"suggestions\": [<strings>]}. "
        "Do not include any additional text or code fences. "
        "Analyze this job posting: "
        f"{req.posting}"
    )
    
    try:
        # Call Claude API for analysis
        text = await claude_api.send_message(prompt)
        text = text.strip()
        
        # Extract JSON payload
        if not text.startswith('{'):
            m = re.search(r'\{.*\}', text, re.S)
            if m:
                text = m.group(0)
        data = json.loads(text)
        score = int(data.get("score", 0))
        suggestions = data.get("suggestions", [])
    except QuotaExceededError as qe:
        # Quota error: return fallback
        return AnalyzeResponse(score=0, suggestions=[str(qe)])
    except Exception:
        score = 0
        suggestions = ["Unable to analyze posting"]
    return AnalyzeResponse(score=score, suggestions=suggestions)

# New endpoint for analyzing job description content and determining enhancement mode
class JobDescriptionAnalysisRequest(BaseModel):
    job_description: str
    company_name: str | None = None
    job_title: str | None = None
    location: str | None = None

@app.post("/api/analyze/job-description")
async def analyze_job_description_content(request: JobDescriptionAnalysisRequest):
    """Analyze job description content and determine optimal enhancement mode"""
    try:
        # Create a request dict for the intelligent enhancer
        request_dict = {
            'job_description': request.job_description,
            'company_name': request.company_name or '',
            'job_title': request.job_title or '',
            'location': request.location or ''
        }
        
        # Analyze with intelligent enhancer
        analysis_result = intelligent_enhancer.analyze_and_enhance(request_dict)
        
        return {
            "mode": analysis_result["mode"],
            "strategy": analysis_result["strategy"],
            "parsed_job_description": analysis_result["parsed_job_description"],
            "form_analysis": analysis_result["form_analysis"],
            "recommendations": analysis_result["recommendations"]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing job description: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Routes
# Main routes
@app.get("/")
def get_ui():
    """Returns the user interface"""
    try:
        logger.debug("Loading user interface")
        with open(TEMPLATES_DIR / "index.html", "r", encoding="utf-8") as file:
            content = file.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logger.error(f"Error loading interface: {str(e)}")
        raise HTTPException(status_code=500, detail="Error loading the interface")

# Routes API
@app.get("/api/models")
async def get_models():
    """Returns the list of available models"""
    try:
        logger.debug("Retrieving models")
        
        if not AVAILABLE_MODELS:
            logger.warning("No models configured")
            return JSONResponse(content={"models": []})
            
        models = [
            {"id": model_id, "name": model_name} 
            for model_id, model_name in AVAILABLE_MODELS.items()
        ]
        
        logger.info(f"Models returned: {models}")
        return JSONResponse(content={"models": models})
        
    except Exception as e:
        logger.error(f"Error retrieving models: {str(e)}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
    
@app.get("/api/settings")
async def get_settings_api():
    """Retrieve user preferences"""
    try:
        prefs_file = DATA_DIR / "user_prefs.json"
        if prefs_file.exists():
            with open(prefs_file, "r", encoding="utf-8") as f:
                prefs = json.load(f)
        else:
            prefs = {}
        return JSONResponse(content=prefs)
    except Exception as e:
        logger.error(f"Error retrieving settings: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/settings")
async def update_settings_api(request: Request):
    """Update user preferences"""
    try:
        prefs = await request.json()
        prefs_file = DATA_DIR / "user_prefs.json"
        with open(prefs_file, "w", encoding="utf-8") as f:
            json.dump(prefs, f, ensure_ascii=False, indent=2)
        return JSONResponse(content={"status": "success"})
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/chat/create")
async def create_chat(request: CreateChatRequest):
    """Creates a new conversation"""
    try:
        logger.debug(f"Creating new chat: {request.name}")
        return chat_manager.create_chat(request.name)
    except Exception as e:
        logger.error(f"Error creating chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/chat/{chat_id}/rename")
async def rename_chat(chat_id: int, request: RenameChatRequest):
    """Renames an existing conversation"""
    try:
        logger.debug(f"Renaming chat {chat_id} to {request.name}")
        return chat_manager.rename_chat(chat_id, request.name)
    except ValueError as e:
        logger.error(f"Chat {chat_id} not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error renaming chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat/{chat_id}")
async def delete_chat(chat_id: int):
    """Deletes a conversation"""
    try:
        logger.debug(f"Deleting chat {chat_id}")
        return chat_manager.delete_chat(chat_id)
    except Exception as e:
        logger.error(f"Error deleting chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/{chat_id}/message")
async def send_message(chat_id: int, request: MessageRequest):
    """Sends a message in a conversation"""
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Empty message")
            
        if len(request.message) > 100000:  # Increased limit
            raise HTTPException(status_code=400, detail="Message too long (max 100000 characters)")
        
        # Model verification
        model_id = request.selected_model if request.selected_model in AVAILABLE_MODELS else DEFAULT_MODEL
        logger.debug(f"Using model: {model_id}")
        
        # Retrieve chat history
        history = chat_manager.get_chat_history(chat_id)
        recent_history = history[-5:] if history else []
        
        # Build context
        context = "\n".join([
            f"{'User' if msg['sender'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in recent_history
        ])
        
        full_context = f"{context}\nUser: {request.message}" if context else request.message
        
        # Search knowledge base for relevant context
        kb_context = kb_manager.search_knowledge_base(request.message)
        
        # Send to Claude API
        logger.debug(f"Sending message to model {model_id}")
        response = await claude_api.send_message(full_context, kb_context)
        
        # Save messages to history
        chat_manager.add_message(chat_id, "user", request.message)
        chat_manager.add_message(chat_id, "assistant", response)
        
        return {"response": response}
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/job-posting")
async def generate_job_posting(request: JobPostingRequest):
    """Intelligently generates job posting using enhanced 3-scenario approach"""
    if not request.job_title:
        raise HTTPException(status_code=400, detail="Job title is required")
    
    # Load user preferences for company information
    try:
        prefs_file = DATA_DIR / "user_prefs.json"
        if prefs_file.exists():
            with open(prefs_file, "r", encoding="utf-8") as f:
                prefs = json.load(f)
        else:
            prefs = {}
    except Exception as e:
        logger.error(f"Error loading user preferences: {e}")
        prefs = {}
    
    # Convert request to dict for intelligent enhancement
    request_dict = {
        "job_title": request.job_title,
        "job_description": request.job_description,  # Main field for complete job descriptions
        "company_name": request.company_name,
        "location": request.location,
        "experience_level": request.experience_level,
        "employment_type": request.employment_type,
        "job_overview": request.job_overview,
        "responsibilities": request.responsibilities,
        "team_intro": request.team_intro,
        "required_skills": request.required_skills,
        "education_requirements": request.education_requirements,
        "experience_details": request.experience_details,
        "certifications": request.certifications,
        "include_salary": request.include_salary,
        "salary_range": request.salary_range,
        "benefits": request.benefits,
        "perks": request.perks,
        "platform": request.platform,
        "length": request.length,
        "application_deadline": request.application_deadline,
        "application_deadline_date": request.application_deadline_date,
        "keywords": request.keywords
    }
    
    # Apply intelligent enhancement
    try:
        enhancement_result = intelligent_enhancer.analyze_and_enhance(request_dict)
        enhanced_context = enhancement_result["enhanced_context"]
        mode = enhancement_result["mode"]
        
        logger.info(f"Using intelligent enhancement mode: {mode}")
        
    except Exception as e:
        logger.error(f"Error in intelligent enhancement, falling back to standard: {e}")
        # Fallback to standard generation
        enhanced_context = build_standard_context(request, prefs)
        mode = "fallback"
    
    # Add company information if not already included
    if not any("Company:" in line for line in enhanced_context.split('\n')):
        company_parts = []
        if prefs.get("company_name"):
            company_parts.append(f"Company: {prefs['company_name']}")
        if prefs.get("industry"):
            company_parts.append(f"Industry: {prefs['industry']}")
        if prefs.get("about_company"):
            company_parts.append(f"About the Company: {prefs['about_company']}")
        
        if company_parts:
            enhanced_context = "\n".join(company_parts) + "\n\n" + enhanced_context
    
    # Add platform and length instructions
    if request.platform:
        platform_instructions = get_platform_instructions(request.platform)
        enhanced_context += f"\n\n{platform_instructions}"
    
    if request.length:
        length_instructions = get_length_instructions(request.length)
        enhanced_context += f"\n\n{length_instructions}"
    
    # Final generation instructions
    enhanced_context += """

FINAL GENERATION INSTRUCTIONS:
- Create a compelling, professional job posting
- Use anti-bias approach incorporating multiple knowledge sources
- Ensure proper formatting with line breaks after bullet points
- Include clear sections: title, overview, responsibilities, qualifications, benefits
- Make content unique, engaging, and platform-optimized
- Incorporate all provided information seamlessly"""
    
    # Stream response with intelligent enhancement
    async def event_stream():
        try:
            full_response = ""
            # Add mode indicator at the beginning
            mode_indicator = get_mode_indicator(mode)
            yield mode_indicator
            
            async for chunk in claude_api.send_message_stream(enhanced_context):
                full_response += chunk
                yield chunk
            
        except QuotaExceededError as e:
            yield f"\n[Error: {e}]"
        except Exception as e:
            yield f"\n[Error: {e}]"
    
    return StreamingResponse(event_stream(), media_type="text/plain")

def build_standard_context(request: JobPostingRequest, prefs: dict) -> str:
    """Fallback method to build standard context"""
    prompt_parts = ["Standard Job Posting Generation"]
    
    if request.job_title:
        prompt_parts.append(f"Position: {request.job_title}")
    
    location = request.location or prefs.get("location")
    if location:
        prompt_parts.append(f"Location: {location}")
    
    if request.experience_level:
        prompt_parts.append(f"Experience Level: {request.experience_level}")
    if request.employment_type:
        prompt_parts.append(f"Employment Type: {request.employment_type}")
    if request.job_overview:
        prompt_parts.append(f"Job Overview: {request.job_overview}")
    
    return "\n".join(prompt_parts)

def get_platform_instructions(platform: str) -> str:
    """Get platform-specific instructions"""
    pf = platform.strip().lower()
    
    if 'linkedin' in pf:
        return """PLATFORM: LinkedIn
- Use LinkedIn-specific formatting with emojis (🔹 ✅ 🚀)
- Keep paragraphs very short for mobile reading
- Include engaging headlines and company culture
- Optimize for social media sharing"""
    elif 'indeed' in pf:
        return """PLATFORM: Indeed
- Include brief summary at the top
- Highlight keywords for search optimization
- Use clear bullets for requirements
- Focus on practical job information"""
    elif 'glassdoor' in pf:
        return """PLATFORM: Glassdoor
- Provide compelling company overview
- Include transparent salary details
- Focus on company culture and values
- Address work-life balance"""
    else:
        return f"PLATFORM: {platform} - Use professional formatting appropriate for this platform"

def get_length_instructions(length: str) -> str:
    """Get length-specific instructions"""
    length_lower = length.strip().lower()
    
    if length_lower == 'long':
        return "LENGTH: Comprehensive - Include detailed sections with thorough explanations"
    elif length_lower == 'standard':
        return "LENGTH: Standard - Balanced detail with clear, concise sections"
    elif length_lower == 'short':
        return "LENGTH: Concise - Key information only with bullet points and essential details"
    else:
        return f"LENGTH: {length}"

def get_mode_indicator(mode: str) -> str:
    """Get user-friendly mode indicator"""
    # Return empty string to eliminate all scenario mentions
    return ""

@app.get("/api/chat/list")
async def get_chat_list():
    """Retrieves the list of conversations"""
    try:
        logger.debug("Retrieving chat list")
        return chat_manager.get_chat_list()
    except Exception as e:
        logger.error(f"Error retrieving chat list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/{chat_id}/history")
async def get_chat_history(chat_id: int):
    """Retrieves the chat history for a conversation"""
    try:
        logger.debug(f"Retrieving history for chat {chat_id}")
        history = chat_manager.get_chat_history(chat_id)
        if history is None:
            raise HTTPException(status_code=404, detail=f"Chat {chat_id} not found")
        return history
    except Exception as e:
        logger.error(f"Error retrieving history for chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Intelligent Job Description Analysis Endpoint
@app.post("/api/analyze-job-description")
async def analyze_job_description(request: Request):
    """Analyze job description content and provide intelligent enhancement suggestions"""
    try:
        data = await request.json()
        
        # Extract job posting request data
        job_posting_request = {
            "job_title": data.get("job_title", ""),
            "job_overview": data.get("job_overview", ""),
            "platform": data.get("platform", ""),
            "location": data.get("location", ""),
            "experience_level": data.get("experience_level", ""),
            "employment_type": data.get("employment_type", ""),
            "responsibilities": data.get("responsibilities", []),
            "required_skills": data.get("required_skills", ""),
            "education_requirements": data.get("education_requirements", ""),
            "certifications": data.get("certifications", ""),
            "benefits": data.get("benefits", []),
            "perks": data.get("perks", ""),
            "include_salary": data.get("include_salary", False),
            "salary_range": data.get("salary_range", ""),
            "application_deadline": data.get("application_deadline"),
            "application_deadline_date": data.get("application_deadline_date"),
            "keywords": data.get("keywords", "")
        }
        
        # Perform intelligent analysis
        analysis_result = intelligent_enhancer.analyze_and_enhance(job_posting_request)
        
        return JSONResponse(content={
            "analysis": analysis_result,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Error analyzing job description: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Text Formatting Endpoint
@app.post("/api/format-text")
async def format_text(request: Request):
    """Format text to ensure proper LinkedIn formatting"""
    try:
        data = await request.json()
        text = data.get("text", "")
        
        if not text:
            return JSONResponse(content={"error": "No text provided"}, status_code=400)
        
        # Format the text
        formatted_text = TextFormatter.format_linkedin_text(text)
        
        # Validate formatting
        validation = TextFormatter.validate_formatting(formatted_text)
        
        return JSONResponse(content={
            "formatted_text": formatted_text,
            "validation": validation,
            "original_length": len(text),
            "formatted_length": len(formatted_text)
        })
        
    except Exception as e:
        logger.error(f"Error formatting text: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Bias Analysis Endpoint
@app.post("/api/analyze-bias")
async def analyze_search_bias(request: Request):
    """Analyze potential bias in search results"""
    try:
        data = await request.json()
        query = data.get("query", "")
        n_results = data.get("n_results", 5)
        
        if not query:
            return JSONResponse(content={"error": "No query provided"}, status_code=400)
        
        # Get bias analysis from vector store
        vector_store = kb_manager.vector_store
        bias_analysis = vector_store.analyze_search_bias(query, n_results)
        
        if "error" in bias_analysis:
            return JSONResponse(content=bias_analysis, status_code=500)
        
        return JSONResponse(content={
            "query": query,
            "bias_analysis": bias_analysis,
            "recommendations": generate_bias_recommendations(bias_analysis)
        })
        
    except Exception as e:
        logger.error(f"Error analyzing bias: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

def generate_bias_recommendations(bias_analysis: dict) -> list:
    """Generate recommendations based on bias analysis"""
    recommendations = []
    
    if bias_analysis.get("bias_detected", False):
        recommendations.append("⚠️ Bias detected: Results dominated by single source")
        recommendations.append("✅ Use balanced retrieval to improve source diversity")
    
    unbalanced_diversity = bias_analysis["unbalanced"]["source_distribution"]["diversity_score"]
    balanced_diversity = bias_analysis["balanced"]["source_distribution"]["diversity_score"]
    
    if balanced_diversity > unbalanced_diversity:
        improvement = bias_analysis["balanced"]["diversity_improvement"]
        recommendations.append(f"✅ Balancing improved diversity by {improvement:.3f}")
    
    if unbalanced_diversity < 0.3:
        recommendations.append("🚨 Very low source diversity - consider expanding knowledge base")
    elif unbalanced_diversity < 0.5:
        recommendations.append("⚠️ Moderate source diversity - balanced retrieval recommended")
    else:
        recommendations.append("✅ Good source diversity")
    
    return recommendations

# Knowledge Base Management Endpoints
@app.get("/api/knowledge-base/stats")
async def get_kb_stats():
    """Get knowledge base statistics"""
    try:
        stats = kb_manager.get_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Error getting KB stats: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/knowledge-base/reload")
async def reload_knowledge_base():
    """Reload the knowledge base from files"""
    try:
        success = kb_manager.load_knowledge_base()
        if success:
            return JSONResponse(content={"status": "success", "message": "Knowledge base reloaded successfully"})
        else:
            return JSONResponse(content={"status": "error", "message": "Failed to reload knowledge base"}, status_code=500)
    except Exception as e:
        logger.error(f"Error reloading KB: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Entry point for direct startup
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Claude Job Posting server")
    uvicorn.run(
        app,
        host="127.0.0.1", 
        port=8001,  # Different port from OpenAI version
        reload=True,
        log_level="debug"
    )