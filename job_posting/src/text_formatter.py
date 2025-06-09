import re
import logging

logger = logging.getLogger(__name__)

class TextFormatter:
    """Text formatter to ensure proper LinkedIn formatting"""
    
    @staticmethod
    def format_linkedin_text(text: str) -> str:
        """
        Format text to ensure proper LinkedIn bullet point formatting
        
        Args:
            text: Raw text from Claude
            
        Returns:
            Properly formatted text with correct line breaks
        """
        try:
            # Split text into lines
            lines = text.split('\n')
            formatted_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    formatted_lines.append('')
                    continue
                
                # Check if line contains multiple bullet points
                if TextFormatter._has_multiple_bullets(line):
                    # Split multiple bullets into separate lines
                    split_bullets = TextFormatter._split_bullet_points(line)
                    formatted_lines.extend(split_bullets)
                else:
                    formatted_lines.append(line)
            
            # Join lines back together
            formatted_text = '\n'.join(formatted_lines)
            
            # Ensure proper spacing around sections
            formatted_text = TextFormatter._fix_section_spacing(formatted_text)
            
            logger.info("Text formatting completed")
            return formatted_text
            
        except Exception as e:
            logger.error(f"Error formatting text: {e}")
            return text  # Return original text if formatting fails
    
    @staticmethod
    def _has_multiple_bullets(line: str) -> bool:
        """Check if a line contains multiple bullet points"""
        # Common bullet emojis used in LinkedIn posts
        bullet_emojis = ['🔹', '✅', '📊', '🎯', '💰', '🚀', '🌍', '📋']
        
        count = 0
        for emoji in bullet_emojis:
            count += line.count(emoji)
        
        return count > 1
    
    @staticmethod
    def _split_bullet_points(line: str) -> list:
        """Split a line with multiple bullet points into separate lines"""
        bullet_emojis = ['🔹', '✅', '📊', '🎯', '💰', '🚀', '🌍', '📋']
        
        # Find all bullet positions
        bullet_positions = []
        for emoji in bullet_emojis:
            pos = 0
            while True:
                pos = line.find(emoji, pos)
                if pos == -1:
                    break
                bullet_positions.append((pos, emoji))
                pos += len(emoji)
        
        # Sort by position
        bullet_positions.sort(key=lambda x: x[0])
        
        if len(bullet_positions) <= 1:
            return [line]
        
        # Split the line at bullet positions
        split_lines = []
        for i, (pos, emoji) in enumerate(bullet_positions):
            if i == len(bullet_positions) - 1:
                # Last bullet point - take rest of line
                bullet_text = line[pos:].strip()
            else:
                # Take text until next bullet
                next_pos = bullet_positions[i + 1][0]
                bullet_text = line[pos:next_pos].strip()
            
            if bullet_text:
                split_lines.append(bullet_text)
        
        return split_lines
    
    @staticmethod
    def _fix_section_spacing(text: str) -> str:
        """Ensure proper spacing between sections"""
        # Add extra line break before major sections
        section_headers = [
            'About Vodafone', 'The Opportunity', 'What You\'ll Do:', 
            'What We\'re Looking For:', 'Success Metrics:', 'Why Vodafone?',
            'Interview Process:', 'Ready to Connect'
        ]
        
        for header in section_headers:
            # Ensure there's a blank line before section headers
            text = re.sub(f'([^\n])\n({re.escape(header)})', r'\1\n\n\2', text)
        
        # Clean up excessive blank lines (max 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    @staticmethod
    def validate_formatting(text: str) -> dict:
        """
        Validate the formatting of the generated text
        
        Returns:
            Dict with validation results
        """
        issues = []
        
        # Check for bullet points on same line
        lines = text.split('\n')
        bullet_emojis = ['🔹', '✅', '📊', '🎯', '💰', '🚀', '🌍', '📋']
        
        for i, line in enumerate(lines, 1):
            bullet_count = sum(line.count(emoji) for emoji in bullet_emojis)
            if bullet_count > 1:
                issues.append(f"Line {i}: Multiple bullet points on same line")
        
        # Check for proper emoji usage
        if not any(emoji in text for emoji in bullet_emojis):
            issues.append("No LinkedIn-style emojis found")
        
        # Check for section headers
        required_sections = ['About', 'Opportunity', 'Looking For']
        found_sections = []
        for section in required_sections:
            if section.lower() in text.lower():
                found_sections.append(section)
        
        missing_sections = set(required_sections) - set(found_sections)
        if missing_sections:
            issues.append(f"Missing sections: {', '.join(missing_sections)}")
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'bullet_count': sum(text.count(emoji) for emoji in bullet_emojis),
            'section_count': len(found_sections)
        }