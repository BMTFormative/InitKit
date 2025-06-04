import logging
from typing import Dict, Any, Optional
from dataclasses import asdict
from .job_description_parser import JobDescriptionParser, ParsedJobDescription
from .knowledge_base import KnowledgeBaseManager

logger = logging.getLogger(__name__)

class IntelligentJobEnhancer:
    """
    Intelligent job posting enhancement service that handles three scenarios:
    1. Brief overview enhancement
    2. Complete job description enhancement  
    3. Hybrid form + JD enhancement
    """
    
    def __init__(self, kb_manager: KnowledgeBaseManager):
        self.parser = JobDescriptionParser()
        self.kb_manager = kb_manager
    
    def analyze_and_enhance(self, job_posting_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for intelligent job posting enhancement
        
        Args:
            job_posting_request: Standard job posting request dict
            
        Returns:
            Enhanced request with parsing info and improvement context
        """
        try:
            job_title = job_posting_request.get("job_title", "")
            # Prioritize job_description over job_overview for complete JDs
            job_content = job_posting_request.get("job_description", "") or job_posting_request.get("job_overview", "")
            platform = job_posting_request.get("platform", "")
            
            # Parse the job content
            parsed_jd = self.parser.parse_job_description(job_content, job_title)
            
            # Determine enhancement mode
            enhancement_mode = self._determine_enhancement_mode(job_posting_request, parsed_jd)
            
            # Create enhanced context
            enhanced_context = self._create_enhanced_context(
                job_posting_request, 
                parsed_jd, 
                enhancement_mode,
                platform
            )
            
            # Generate parsing summary for UI feedback
            parsing_summary = self.parser.generate_parsing_summary(parsed_jd)
            
            return {
                "mode": enhancement_mode,
                "parsed_job_description": asdict(parsed_jd),
                "enhanced_context": enhanced_context,
                "parsing_summary": parsing_summary,
                "original_request": job_posting_request,
                "recommendations": self._generate_recommendations(enhancement_mode, parsed_jd)
            }
            
        except Exception as e:
            logger.error(f"Error in intelligent enhancement: {e}")
            # Fallback to original request
            return {
                "mode": "fallback",
                "enhanced_context": self._build_standard_context(job_posting_request),
                "parsing_summary": {"error": str(e)},
                "original_request": job_posting_request,
                "recommendations": ["Using standard form-based generation due to parsing error."]
            }
    
    def _determine_enhancement_mode(self, request: Dict[str, Any], parsed_jd: ParsedJobDescription) -> str:
        """
        Determine which enhancement mode to use based on content analysis
        
        Returns:
            "scenario_a": Quick enhancement (paste full JD)
            "scenario_b": Form-based generation (traditional)
            "scenario_c": Hybrid enhancement (parsed JD + form data)
        """
        job_overview = request.get("job_overview", "")
        
        # Check if form fields are filled
        form_fields_filled = sum(1 for key in [
            "responsibilities", "required_skills", "education_requirements", 
            "certifications", "benefits", "perks"
        ] if request.get(key))
        
        # Scenario determination logic
        if parsed_jd.mode == "full_jd" and form_fields_filled == 0:
            return "scenario_a"  # Complete JD pasted, no form data
        elif parsed_jd.mode == "brief_overview" and form_fields_filled > 0:
            return "scenario_b"  # Brief overview + detailed form
        elif parsed_jd.mode in ["structured", "full_jd"] and form_fields_filled > 0:
            return "scenario_c"  # Hybrid: parsed content + form enhancements
        elif len(job_overview) > 500:
            return "scenario_a"  # Long content, treat as full JD
        else:
            return "scenario_b"  # Default to form-based
    
    def _create_enhanced_context(self, request: Dict[str, Any], parsed_jd: ParsedJobDescription, 
                               mode: str, platform: str) -> str:
        """Create enhanced context for Claude based on the determined mode"""
        
        context_parts = []
        
        # Add mode-specific context (clean, no scenario mentions)
        if mode == "scenario_a":
            context_parts.append("CONTENT ENHANCEMENT TASK:")
            context_parts.append("Improve and optimize the following job description with best practices")
            context_parts.append(f"Source Content:\n{parsed_jd.original_content}")
            
        elif mode == "scenario_b":
            context_parts.append("JOB POSTING CREATION TASK:")
            context_parts.append("Create a comprehensive job posting from the provided information")
            context_parts.extend(self._build_form_context(request))
            
        elif mode == "scenario_c":
            context_parts.append("CONTENT OPTIMIZATION TASK:")
            context_parts.append("Enhance and merge the following content with additional details")
            context_parts.append(f"Base Content:\n{parsed_jd.job_overview or 'N/A'}")
            
            # Add parsed sections
            if parsed_jd.responsibilities:
                context_parts.append(f"Extracted Responsibilities:\n" + 
                                   "\n".join(f"- {r}" for r in parsed_jd.responsibilities))
            
            if parsed_jd.qualifications:
                context_parts.append(f"Extracted Qualifications:\n" + 
                                   "\n".join(f"- {q}" for q in parsed_jd.qualifications))
            
            # Add form enhancements
            context_parts.extend(self._build_form_context(request, exclude_parsed=True))
        
        # Add extracted metadata
        metadata_parts = []
        if parsed_jd.employment_type:
            metadata_parts.append(f"Employment Type: {parsed_jd.employment_type}")
        if parsed_jd.experience_level:
            metadata_parts.append(f"Experience Level: {parsed_jd.experience_level}")
        if parsed_jd.salary_range:
            metadata_parts.append(f"Salary Range: {parsed_jd.salary_range}")
        if parsed_jd.location:
            metadata_parts.append(f"Location: {parsed_jd.location}")
        
        if metadata_parts:
            context_parts.append("Extracted Metadata:")
            context_parts.extend(metadata_parts)
        
        # Add knowledge base context
        kb_context = self._get_knowledge_base_context(request, platform)
        if kb_context:
            context_parts.append("\nRelevant Knowledge Base Context:")
            context_parts.append(kb_context)
        
        # Add enhancement instructions
        context_parts.extend(self._get_enhancement_instructions(mode, platform, parsed_jd))
        
        # Add final system override
        context_parts.append("")
        context_parts.append("SYSTEM OVERRIDE - FINAL INSTRUCTION:")
        context_parts.append("You are now writing AS THE COMPANY. Do not mention AI, scenarios, processing, or generation.")
        context_parts.append("Begin your response immediately with the job posting content. No meta-text allowed.")
        context_parts.append("FORBIDDEN WORDS IN OUTPUT: scenario, mode, enhancement, generation, analysis, based on, here is, I will, this is, generated, enhanced, processed, created")
        
        return "\n\n".join(context_parts)
    
    def _build_form_context(self, request: Dict[str, Any], exclude_parsed: bool = False) -> list:
        """Build context from form fields"""
        context_parts = []
        
        # Basic information
        if request.get("job_title"):
            context_parts.append(f"Position: {request['job_title']}")
        if request.get("location"):
            context_parts.append(f"Location: {request['location']}")
        if request.get("experience_level"):
            context_parts.append(f"Experience Level: {request['experience_level']}")
        if request.get("employment_type"):
            context_parts.append(f"Employment Type: {request['employment_type']}")
        
        # Detailed sections (only if not excluding parsed content)
        if not exclude_parsed or not request.get("responsibilities"):
            if request.get("responsibilities"):
                resp_text = '\n'.join(f"- {item}" for item in request['responsibilities'])
                context_parts.append(f"Responsibilities:\n{resp_text}")
        
        if request.get("team_intro"):
            context_parts.append(f"Team / Organization: {request['team_intro']}")
        if request.get("required_skills"):
            context_parts.append(f"Required Skills: {request['required_skills']}")
        if request.get("education_requirements"):
            context_parts.append(f"Education Requirements: {request['education_requirements']}")
        if request.get("certifications"):
            context_parts.append(f"Certifications: {request['certifications']}")
        
        # Benefits and compensation
        if request.get("include_salary") and request.get("salary_range"):
            context_parts.append(f"Salary Range: {request['salary_range']}")
        if request.get("benefits"):
            context_parts.append(f"Benefits: {', '.join(request['benefits'])}")
        if request.get("perks"):
            context_parts.append(f"Perks: {request['perks']}")
        
        # Timeline
        if request.get("application_deadline_date"):
            context_parts.append(f"Application Deadline: {request['application_deadline_date']}")
        elif request.get("application_deadline"):
            context_parts.append(f"Application Deadline: {request['application_deadline']} days")
        
        if request.get("keywords"):
            context_parts.append(f"Keywords to highlight: {request['keywords']}")
        
        return context_parts
    
    def _get_knowledge_base_context(self, request: Dict[str, Any], platform: str) -> str:
        """Get relevant knowledge base context"""
        try:
            # Build search query based on request content
            search_terms = []
            if platform:
                search_terms.append(platform)
            if request.get("job_title"):
                search_terms.append("job posting")
            
            search_query = " ".join(search_terms) if search_terms else "job posting best practices"
            
            # Search knowledge base with platform specificity
            context = self.kb_manager.search_knowledge_base(search_query, platform.lower() if platform else None)
            
            return context[:1500]  # Limit context size
            
        except Exception as e:
            logger.error(f"Error getting KB context: {e}")
            return ""
    
    def _get_enhancement_instructions(self, mode: str, platform: str, parsed_jd: ParsedJobDescription) -> list:
        """Get mode-specific enhancement instructions"""
        instructions = []
        
        # Platform-specific instructions
        if platform and platform.lower() == "linkedin":
            instructions.append(
                "PLATFORM: LinkedIn - Use LinkedIn-specific formatting with emojis, "
                "short paragraphs, and engaging content optimized for social media."
            )
        elif platform:
            instructions.append(f"PLATFORM: {platform} - Use professional formatting appropriate for this platform.")
        
        # Enhancement instructions (clean, no scenario mentions)
        if mode == "scenario_a":
            instructions.extend([
                "ENHANCEMENT APPROACH:",
                "- Preserve the core content and structure",
                "- Improve formatting and readability", 
                "- Add platform-specific optimizations",
                "- Enhance language for better engagement",
                "- Ensure all sections are well-structured",
                "- Add missing elements if beneficial"
            ])
        elif mode == "scenario_b":
            instructions.extend([
                "CONTENT CREATION:",
                "- Create comprehensive job posting from provided data",
                "- Use knowledge base best practices",
                "- Ensure professional structure and formatting", 
                "- Include all provided information seamlessly"
            ])
        elif mode == "scenario_c":
            instructions.extend([
                "CONTENT OPTIMIZATION:",
                "- Merge existing content with additional information",
                "- Prioritize new data where applicable",
                "- Enhance all sections with best practices",
                "- Create cohesive, professional final output",
                "- Ensure no information is lost or duplicated"
            ])
        
        # Quality and output instructions
        instructions.extend([
            "QUALITY REQUIREMENTS:",
            "- Use anti-bias approach incorporating multiple knowledge sources",
            "- Ensure proper formatting with line breaks after bullet points", 
            "- Create engaging, professional content",
            "- Include clear sections: title, overview, responsibilities, qualifications, benefits",
            "- Make content unique and compelling",
            "",
            "ABSOLUTELY CRITICAL - OUTPUT FORMAT:",
            "- NEVER mention 'Scenario', 'Mode', 'Enhancement', 'Generation', 'Analysis', or any technical process",
            "- NEVER include system messages like 'Scenario A:', 'Scenario B:', 'Generating...', 'Based on...', 'Enhanced...', etc.",
            "- NEVER add meta-commentary or processing descriptions",
            "- NEVER explain what you are doing or how you are processing the request",
            "- NEVER start with phrases like 'Here is', 'Based on', 'I will', 'This is', 'Generated', etc.",
            "- START IMMEDIATELY with the job posting title or company name",
            "- RETURN ONLY the final, clean job posting content that can be copied and pasted directly",
            "- WRITE as if you are the company posting the job, not an AI assistant processing a request",
            "- IGNORE all technical aspects and focus solely on creating compelling job posting content",
            "- NO TECHNICAL LANGUAGE: Avoid words like 'enhance', 'generate', 'create', 'process', 'analyze' in your output"
        ])
        
        return instructions
    
    def _build_standard_context(self, request: Dict[str, Any]) -> str:
        """Fallback method to build standard context"""
        context_parts = ["Standard Job Posting Generation"]
        context_parts.extend(self._build_form_context(request))
        return "\n\n".join(context_parts)
    
    def _generate_recommendations(self, mode: str, parsed_jd: ParsedJobDescription) -> list:
        """Generate user-facing recommendations based on analysis"""
        recommendations = []
        
        if mode == "scenario_a":
            recommendations.append("🚀 Complete job description detected! Optimizing with best practices.")
            if parsed_jd.confidence > 0.8:
                recommendations.append(f"✨ High confidence analysis ({parsed_jd.confidence:.1%}) - extracted {len(parsed_jd.detected_sections)} sections.")
        
        elif mode == "scenario_b":
            recommendations.append("📝 Creating comprehensive job posting from your detailed input.")
            
        elif mode == "scenario_c":
            recommendations.append("🔀 Combining your content with additional form details.")
            recommendations.append("💡 Pro tip: Check the auto-filled form fields extracted from your content.")
        
        # Add specific recommendations based on parsed content
        if parsed_jd.detected_sections:
            sections_text = ", ".join(parsed_jd.detected_sections)
            recommendations.append(f"📋 Detected sections: {sections_text}")
        
        if parsed_jd.mode == "full_jd" and len(parsed_jd.parsing_notes) == 0:
            recommendations.append("✅ Clean analysis - your content is well-structured!")
        
        return recommendations