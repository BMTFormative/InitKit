"""
Job Posting Generator - Simplified Files API Version
Clean architecture with Files API integration
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from datetime import date, datetime
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Job Posting Generator - Files API",
    description="Simplified job posting generation using Claude Files API",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Import components
from src.files_api_client import FilesAPIClient
from config.settings import AVAILABLE_MODELS, DEFAULT_MODEL

# Initialize Files API client
files_api_client = FilesAPIClient()
logger.info("Files API client initialized successfully")

# Data models
class JobPostingRequest(BaseModel):
    job_title: str
    job_description: str | None = None  # For pasted complete job descriptions
    company_name: str | None = None
    location: str | None = None
    experience_level: str | None = None
    employment_type: str | None = None
    job_overview: str | None = None
    responsibilities: list[str] | str | None = None  # Can be list or string from textarea
    team_intro: str | None = None
    required_skills: str | None = None
    education_requirements: str | None = None
    experience_details: str | None = None
    certifications: str | None = None
    include_salary: bool = False
    salary_range: str | None = None
    benefits: list[str] | str | None = None  # Can be list or string
    perks: str | None = None
    platform: str = "linkedin"
    length: str = "standard"
    application_deadline: int | None = None
    application_deadline_date: date | None = None
    keywords: str | None = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_title": "Machine Learning Engineer",
                "platform": "linkedin",
                "length": "standard"
            }
        }

class TokenUsageStats(BaseModel):
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_breakdown: dict
    usage_report: str
    files_api_used: bool

class JobPostingResponse(BaseModel):
    job_posting: str
    usage_stats: TokenUsageStats

# Routes
@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    """Serve the main interface"""
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logger.error(f"Error loading homepage: {e}")
        raise HTTPException(status_code=500, detail="Error loading interface")

@app.get("/api/models")
async def get_available_models():
    """Get available Claude models"""
    try:
        models = [
            {"id": model_id, "name": model_name}
            for model_id, model_name in AVAILABLE_MODELS.items()
        ]
        return {"models": models}
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return {"error": str(e)}

@app.get("/api/files-api/status")
async def get_files_api_status():
    """Get Files API status"""
    try:
        status = files_api_client.get_status()
        return status
    except Exception as e:
        logger.error(f"Error getting Files API status: {e}")
        return {"error": str(e)}

@app.post("/api/generate/job-posting", response_model=JobPostingResponse)
async def generate_job_posting(request: JobPostingRequest):
    """Generate job posting using Files API with token counting"""
    
    if not request.job_title:
        raise HTTPException(status_code=400, detail="Job title is required")
    
    # Load user preferences for company information
    try:
        prefs_file = Path("data/user_prefs.json")
        if prefs_file.exists():
            with open(prefs_file, "r", encoding="utf-8") as f:
                prefs = json.load(f)
        else:
            prefs = {}
    except Exception as e:
        logger.error(f"Error loading user preferences: {e}")
        prefs = {}
    
    # Check if this is a complete job description (Scenario A) or form-based (Scenario B/C)
    if request.job_description and len(request.job_description.strip()) > 200:
        # Scenario A: Complete job description enhancement
        message_parts = [
            "Please enhance and optimize this job description for best practices and platform-specific formatting:",
            f"\nOriginal Job Description:\n{request.job_description}",
            f"\nJob Title: {request.job_title}"
        ]
        
        # Add company information if available
        company_name = request.company_name or prefs.get("company_name", "")
        if company_name:
            message_parts.append(f"Company: {company_name}")
        
        if prefs.get("industry"):
            message_parts.append(f"Industry: {prefs['industry']}")
        
        if prefs.get("about_company"):
            message_parts.append(f"About Company: {prefs['about_company']}")
            
    else:
        # Scenario B/C: Form-based generation
        message_parts = [f"Create a professional job posting for: {request.job_title}"]
        
        # Add company information
        company_name = request.company_name or prefs.get("company_name", "")
        if company_name:
            message_parts.append(f"Company: {company_name}")
        
        if prefs.get("industry"):
            message_parts.append(f"Industry: {prefs['industry']}")
        
        if prefs.get("about_company"):
            message_parts.append(f"About the Company: {prefs['about_company']}")
        
        # Add location
        location = request.location or prefs.get("location", "")
        if location:
            message_parts.append(f"Location: {location}")
        
        if request.experience_level:
            message_parts.append(f"Experience Level: {request.experience_level}")
        if request.employment_type:
            message_parts.append(f"Employment Type: {request.employment_type}")
        if request.job_overview:
            message_parts.append(f"Job Overview: {request.job_overview}")
        if request.team_intro:
            message_parts.append(f"Team/Organization: {request.team_intro}")
        if request.responsibilities:
            if isinstance(request.responsibilities, list):
                message_parts.append(f"Key Responsibilities:\n- " + "\n- ".join(request.responsibilities))
            else:
                # Handle string format from textarea
                resp_lines = [line.strip() for line in str(request.responsibilities).split('\n') if line.strip()]
                if resp_lines:
                    message_parts.append(f"Key Responsibilities:\n- " + "\n- ".join(resp_lines))
        if request.required_skills:
            message_parts.append(f"Required Skills: {request.required_skills}")
        if request.education_requirements:
            message_parts.append(f"Education: {request.education_requirements}")
        if request.experience_details:
            message_parts.append(f"Experience Details: {request.experience_details}")
        if request.certifications:
            message_parts.append(f"Certifications: {request.certifications}")
        if request.include_salary and request.salary_range:
            message_parts.append(f"Salary Range: {request.salary_range}")
        if request.benefits:
            if isinstance(request.benefits, list):
                message_parts.append(f"Benefits: {', '.join(request.benefits)}")
            else:
                message_parts.append(f"Benefits: {request.benefits}")
        if request.perks:
            message_parts.append(f"Perks: {request.perks}")
        if request.application_deadline:
            message_parts.append(f"Application Deadline: {request.application_deadline} days")
        elif request.application_deadline_date:
            message_parts.append(f"Application Deadline: {request.application_deadline_date}")
        if request.keywords:
            message_parts.append(f"Keywords to include: {request.keywords}")
    
    # Platform-specific formatting instructions
    platform_lower = request.platform.lower()
    if "linkedin" in platform_lower:
        message_parts.append("\nPLATFORM: LinkedIn - Use emojis (🔹 ✅ 🚀), short paragraphs for mobile reading, engaging content.")
    elif "indeed" in platform_lower:
        message_parts.append("\nPLATFORM: Indeed - Include brief summary, highlight keywords, use clear bullets.")
    elif "glassdoor" in platform_lower:
        message_parts.append("\nPLATFORM: Glassdoor - Provide company overview, include transparent details, focus on culture.")
    else:
        message_parts.append(f"\nPLATFORM: {request.platform} - Use professional formatting.")
    
    # Length-specific instructions
    if request.length:
        length_lower = request.length.lower()
        if length_lower == 'long':
            message_parts.append("\nLENGTH: Comprehensive - Include detailed sections with thorough explanations")
        elif length_lower == 'standard':
            message_parts.append("\nLENGTH: Standard - Balanced detail with clear, concise sections")
        elif length_lower == 'short':
            message_parts.append("\nLENGTH: Concise - Key information only with bullet points and essential details")
    
    # Final generation instructions
    message_parts.append("""
FINAL GENERATION INSTRUCTIONS:
- Create a compelling, professional job posting
- Use Files API knowledge base best practices
- Ensure proper formatting with line breaks after bullet points
- Include clear sections: title, overview, responsibilities, qualifications, benefits
- Make content unique, engaging, and platform-optimized
- Incorporate all provided information seamlessly""")
    
    message = "\n".join(message_parts)
    
    try:
        # Stream response for progressive display
        async def event_stream():
            try:
                async for chunk in files_api_client.generate_streaming(
                    message=message,
                    platform=request.platform,
                    model=DEFAULT_MODEL
                ):
                    yield chunk
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"\n[Error: {e}]"
        
        return StreamingResponse(event_stream(), media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Error generating job posting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/settings")
async def get_user_settings():
    """Get user preferences"""
    try:
        settings_file = Path("data/user_prefs.json")
        if settings_file.exists():
            with open(settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
        else:
            settings = {}
        return settings
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return {"error": str(e)}

@app.post("/api/settings")
async def update_user_settings(request: Request):
    """Update user preferences"""
    try:
        settings = await request.json()
        settings_file = Path("data/user_prefs.json")
        settings_file.parent.mkdir(exist_ok=True)
        
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        return {"error": str(e)}

@app.post("/api/analyze/tokens")
async def analyze_token_usage(request: Request):
    """Analyze token usage for a message"""
    try:
        data = await request.json()
        message = data.get("message", "")
        model = data.get("model", DEFAULT_MODEL)
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Get token analysis
        analysis = await files_api_client.analyze_tokens(message, model)
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing tokens: {e}")
        return {"error": str(e)}

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
        "Analyze this job posting for quality, completeness, clarity, and effectiveness. "
        "Score from 0-100 where 100 is excellent. Provide 3-5 specific actionable suggestions: "
        f"{req.posting}"
    )
    
    try:
        # Call Files API for analysis using simple message generation
        analysis_result, _ = await files_api_client.generate_with_token_count(
            message='',
            platform="analysis",
            model=req.selected_model or DEFAULT_MODEL
        )
        
        # Extract JSON payload
        text = analysis_result.strip()
        if not text.startswith('{'):
            import re
            m = re.search(r'\{.*\}', text, re.S)
            if m:
                text = m.group(0)
        
        data = json.loads(text)
        score = int(data.get("score", 0))
        suggestions = data.get("suggestions", [])
        
        return AnalyzeResponse(score=score, suggestions=suggestions)
        
    except Exception as e:
        logger.error(f"Error analyzing job posting: {e}")
        # Fallback response
        return AnalyzeResponse(
            score=50, 
            suggestions=["Unable to analyze posting - check API configuration"]
        )

# Models for applying suggestions
class ApplySuggestionsRequest(BaseModel):
    original_posting: str
    suggestions: list[str]
    suggestion_comment: str | None = None

@app.post("/api/verify/files-usage")
async def verify_files_usage():
    """Verify which files are configured and available for Files API"""
    try:
        client_status = files_api_client.get_status()
        
        # Get file IDs configuration
        from config.settings import KNOWLEDGE_BASE_FILES
        
        verification_info = {
            "files_api_active": client_status["files_api_available"],
            "mode": client_status["mode"],
            "configured_files": KNOWLEDGE_BASE_FILES,
            "verification_timestamp": datetime.now().isoformat(),
            "files_api_client_type": "Real Files API" if client_status["files_api_available"] else "Compatibility Mode"
        }
        
        return verification_info
        
    except Exception as e:
        logger.error(f"Error verifying files usage: {e}")
        return {"error": str(e)}

# Token stats endpoint removed per user request

@app.post("/api/generate/apply-suggestions")
async def apply_suggestions(request: ApplySuggestionsRequest):
    """Apply suggestions to improve an existing job posting"""
    if not request.original_posting:
        raise HTTPException(status_code=400, detail="Original posting is required")
    
    # Build improvement message
    message_parts = []
    message_parts.append(f"Original Job Posting:\n{request.original_posting}")
    message_parts.append("\nPlease apply the following suggestions to improve this posting:")
    for suggestion in request.suggestions:
        message_parts.append(f"- {suggestion}")
    
    if request.suggestion_comment:
        message_parts.append(f"\nAdditional instructions: {request.suggestion_comment}")
    
    message_parts.append("\nReturn the complete, improved job posting with clear sections.")
    message = "\n".join(message_parts)
    
    try:
        # Stream improved posting with Files API
        async def improvement_stream():
            try:
                async for chunk in files_api_client.generate_streaming(
                    message=message,
                    platform="improvement",
                    model=DEFAULT_MODEL
                ):
                    yield chunk
            except Exception as e:
                logger.error(f"Improvement streaming error: {e}")
                yield f"\n[Error: {e}]"
        
        return StreamingResponse(improvement_stream(), media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Error applying suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Job Posting Generator Files API",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Job Posting Generator - Files API Version")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )