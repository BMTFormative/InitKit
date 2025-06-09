import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ParsedJobDescription:
    """Structured representation of a parsed job description"""
    mode: str  # "full_jd", "brief_overview", "structured"
    confidence: float  # 0.0-1.0 confidence in parsing accuracy
    
    # Extracted sections
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    
    job_overview: Optional[str] = None
    responsibilities: List[str] = None
    qualifications: List[str] = None
    education_requirements: Optional[str] = None
    benefits: List[str] = None
    salary_range: Optional[str] = None
    
    # Metadata
    original_content: str = ""
    detected_sections: List[str] = None
    parsing_notes: List[str] = None

class JobDescriptionParser:
    """
    Intelligent parser for job descriptions with support for multiple formats.
    Handles scenarios from brief overviews to complete job descriptions.
    """
    
    def __init__(self):
        # Section identifiers for parsing
        self.section_patterns = {
            'responsibilities': [
                r'responsibilities?[:\-]?',
                r'duties[:\-]?',
                r'what you[\'\u2019]?ll do[:\-]?',
                r'role overview[:\-]?',
                r'key tasks?[:\-]?',
                r'your role[:\-]?'
            ],
            'qualifications': [
                r'qualifications?[:\-]?',
                r'requirements?[:\-]?',
                r'what we[\'\u2019]?re looking for[:\-]?',
                r'ideal candidate[:\-]?',
                r'skills? required?[:\-]?',
                r'must have[:\-]?',
                r'experience[:\-]?'
            ],
            'benefits': [
                r'benefits?[:\-]?',
                r'what we offer[:\-]?',
                r'perks?[:\-]?',
                r'compensation[:\-]?',
                r'why join us[:\-]?',
                r'package[:\-]?'
            ],
            'company': [
                r'about us[:\-]?',
                r'about the company[:\-]?',
                r'company overview[:\-]?',
                r'who we are[:\-]?',
                r'our company[:\-]?'
            ]
        }
        
        # Bullet point patterns
        self.bullet_patterns = [
            r'^\s*[-•·*]\s+',  # Standard bullets
            r'^\s*\d+[\.)]\s+',  # Numbered lists
            r'^\s*[a-zA-Z][\.)]\s+',  # Lettered lists
            r'^\s*[🔹✅📊🎯💼🚀]\s*',  # Emoji bullets
        ]
        
        # Employment type indicators
        self.employment_types = {
            'full-time': ['full time', 'full-time', 'fulltime', 'permanent'],
            'part-time': ['part time', 'part-time', 'parttime'],
            'contract': ['contract', 'contractor', 'freelance', 'temporary'],
            'remote': ['remote', 'work from home', 'wfh', 'distributed'],
            'hybrid': ['hybrid', 'flexible', 'mixed']
        }
        
        # Experience level indicators
        self.experience_levels = {
            'entry': ['entry level', 'junior', 'graduate', '0-2 years', 'new grad'],
            'mid': ['mid level', 'intermediate', '3-5 years', '2-5 years'],
            'senior': ['senior', 'lead', '5+ years', '5-8 years', 'experienced'],
            'principal': ['principal', 'staff', 'expert', '8+ years', '10+ years'],
            'director': ['director', 'head of', 'vp', 'vice president', 'executive']
        }
    
    def detect_content_type(self, content: str) -> str:
        """
        Detect the type of content provided
        
        Returns:
            "full_jd": Complete job description with multiple sections
            "brief_overview": Short description or overview
            "structured": Partially structured content
        """
        if not content or len(content.strip()) < 50:
            return "brief_overview"
        
        content_lower = content.lower()
        section_count = 0
        
        # Count detected sections
        for section_type, patterns in self.section_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    section_count += 1
                    break
        
        # Count bullet points
        bullet_count = sum(1 for line in content.split('\n') 
                          if any(re.match(pattern, line) for pattern in self.bullet_patterns))
        
        # Determine content type
        if section_count >= 3 and len(content) > 800:
            return "full_jd"
        elif section_count >= 2 or bullet_count >= 5:
            return "structured"
        else:
            return "brief_overview"
    
    def parse_job_description(self, content: str, job_title: str = "") -> ParsedJobDescription:
        """
        Parse job description content and extract structured information
        
        Args:
            content: Job description text
            job_title: Job title if provided separately
            
        Returns:
            ParsedJobDescription object with extracted information
        """
        try:
            content_type = self.detect_content_type(content)
            confidence = 0.7  # Base confidence
            
            result = ParsedJobDescription(
                mode=content_type,
                confidence=confidence,
                original_content=content,
                detected_sections=[],
                parsing_notes=[]
            )
            
            if content_type == "brief_overview":
                # Simple case - just use as job overview
                result.job_overview = content.strip()
                result.parsing_notes.append("Brief content detected - using as job overview")
                
            elif content_type in ["structured", "full_jd"]:
                # Complex parsing for structured content
                self._parse_structured_content(content, result)
                confidence = 0.9 if content_type == "full_jd" else 0.8
            
            # Extract additional metadata
            self._extract_metadata(content, result)
            
            # Set job title if provided
            if job_title:
                result.job_title = job_title
            
            result.confidence = confidence
            logger.info(f"Parsed job description: mode={content_type}, confidence={confidence}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing job description: {e}")
            # Fallback - treat as brief overview
            return ParsedJobDescription(
                mode="brief_overview",
                confidence=0.5,
                job_overview=content.strip(),
                original_content=content,
                parsing_notes=[f"Parsing error: {str(e)}"]
            )
    
    def _parse_structured_content(self, content: str, result: ParsedJobDescription):
        """Parse structured content into sections"""
        sections = self._split_into_sections(content)
        
        for section_type, section_content in sections.items():
            result.detected_sections.append(section_type)
            
            if section_type == 'responsibilities':
                result.responsibilities = self._extract_bullet_points(section_content)
            elif section_type == 'qualifications':
                result.qualifications = self._extract_bullet_points(section_content)
            elif section_type == 'benefits':
                result.benefits = self._extract_bullet_points(section_content)
            elif section_type == 'company':
                result.job_overview = section_content.strip()
        
        # If no specific overview found, use first paragraph
        if not result.job_overview and content:
            first_paragraph = content.split('\n\n')[0].strip()
            if len(first_paragraph) > 50:
                result.job_overview = first_paragraph
    
    def _split_into_sections(self, content: str) -> Dict[str, str]:
        """Split content into identified sections"""
        sections = {}
        content_lower = content.lower()
        
        for section_type, patterns in self.section_patterns.items():
            for pattern in patterns:
                match = re.search(f'({pattern})', content_lower, re.IGNORECASE)
                if match:
                    start_pos = match.start()
                    
                    # Find content until next section or end
                    section_content = ""
                    remaining_content = content[start_pos:]
                    
                    # Look for next section
                    next_section_pos = len(remaining_content)
                    for other_type, other_patterns in self.section_patterns.items():
                        if other_type != section_type:
                            for other_pattern in other_patterns:
                                other_match = re.search(f'({other_pattern})', remaining_content[50:], re.IGNORECASE)
                                if other_match:
                                    next_section_pos = min(next_section_pos, other_match.start() + 50)
                    
                    section_content = remaining_content[:next_section_pos]
                    # Remove the header line
                    section_lines = section_content.split('\n')[1:]
                    sections[section_type] = '\n'.join(section_lines).strip()
                    break
        
        return sections
    
    def _extract_bullet_points(self, content: str) -> List[str]:
        """Extract bullet points from section content"""
        bullets = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a bullet point
            is_bullet = any(re.match(pattern, line) for pattern in self.bullet_patterns)
            
            if is_bullet:
                # Clean bullet prefix
                cleaned = line
                for pattern in self.bullet_patterns:
                    cleaned = re.sub(pattern, '', cleaned).strip()
                if cleaned:
                    bullets.append(cleaned)
            elif line and not bullets:
                # If no bullets yet, treat as paragraph text
                bullets.append(line)
        
        return bullets[:10]  # Limit to reasonable number
    
    def _extract_metadata(self, content: str, result: ParsedJobDescription):
        """Extract metadata like employment type, experience level, salary"""
        content_lower = content.lower()
        
        # Extract employment type
        for emp_type, keywords in self.employment_types.items():
            if any(keyword in content_lower for keyword in keywords):
                result.employment_type = emp_type.replace('-', ' ').title()
                break
        
        # Extract experience level
        for level, keywords in self.experience_levels.items():
            if any(keyword in content_lower for keyword in keywords):
                if level == 'entry':
                    result.experience_level = "Entry Level (0-2 yrs)"
                elif level == 'mid':
                    result.experience_level = "Mid Level (3-5 yrs)"
                elif level == 'senior':
                    result.experience_level = "Senior (5-8 yrs)"
                elif level == 'principal':
                    result.experience_level = "Principal (8+ yrs)"
                elif level == 'director':
                    result.experience_level = "Director (10+ yrs)"
                break
        
        # Extract salary information
        salary_patterns = [
            r'[\$£€]\s*\d{1,3}(?:,\d{3})*(?:\s*-\s*[\$£€]?\s*\d{1,3}(?:,\d{3})*)?',
            r'\d{1,3}(?:,\d{3})*\s*-\s*\d{1,3}(?:,\d{3})*\s*(?:per year|annually|\/year)',
            r'\d{1,3}k?\s*-\s*\d{1,3}k?\s*(?:per year|annually|\/year)?'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                result.salary_range = match.group(0)
                break
        
        # Extract location
        location_patterns = [
            r'location[:\-]?\s*([^\n\r]{2,50})',
            r'based in[:\-]?\s*([^\n\r]{2,50})',
            r'office[:\-]?\s*([^\n\r]{2,50})'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, content_lower, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                if len(location) > 2 and len(location) < 50:
                    result.location = location.title()
                break
    
    def generate_parsing_summary(self, parsed: ParsedJobDescription) -> Dict[str, Any]:
        """Generate a summary of parsing results for UI feedback"""
        summary = {
            "mode": parsed.mode,
            "confidence": parsed.confidence,
            "detected_sections": parsed.detected_sections,
            "extraction_summary": {},
            "suggestions": [],
            "auto_filled_fields": []
        }
        
        # Count extracted items
        if parsed.responsibilities:
            summary["extraction_summary"]["responsibilities"] = len(parsed.responsibilities)
            summary["auto_filled_fields"].append("responsibilities")
        
        if parsed.qualifications:
            summary["extraction_summary"]["qualifications"] = len(parsed.qualifications)
            summary["auto_filled_fields"].append("qualifications")
        
        if parsed.benefits:
            summary["extraction_summary"]["benefits"] = len(parsed.benefits)
            summary["auto_filled_fields"].append("benefits")
        
        # Add metadata extractions
        if parsed.employment_type:
            summary["auto_filled_fields"].append("employment_type")
        if parsed.experience_level:
            summary["auto_filled_fields"].append("experience_level")
        if parsed.salary_range:
            summary["auto_filled_fields"].append("salary_range")
        if parsed.location:
            summary["auto_filled_fields"].append("location")
        
        # Generate suggestions based on mode
        if parsed.mode == "full_jd":
            summary["suggestions"].append("📋 Complete job description detected! I'll enhance it with best practices.")
            if len(summary["auto_filled_fields"]) > 3:
                summary["suggestions"].append("✨ I've automatically extracted sections - check the form fields below!")
        elif parsed.mode == "structured":
            summary["suggestions"].append("📝 Structured content detected! I'll parse sections and enhance formatting.")
        else:
            summary["suggestions"].append("✍️ Brief overview mode - use the form below for detailed sections.")
        
        return summary