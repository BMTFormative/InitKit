# backend/app/scripts/test_claude_integration.py
"""
Test script for Claude integration
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

async def test_claude_service():
    """Test the Claude service integration"""
    try:
        from services.claude_service import ClaudeService, KnowledgeBaseManager
        from core.config import settings
        
        print("🧪 Testing Claude Integration...")
        print("=" * 50)
        
        # Check environment variables
        claude_key = os.getenv('CLAUDE_API_KEY') or settings.CLAUDE_API_KEY
        if not claude_key:
            print("❌ CLAUDE_API_KEY not found in environment variables")
            print("   Please add CLAUDE_API_KEY=your_key_here to your .env file")
            return False
        
        print("✅ Claude API key found")
        
        # Test knowledge base
        print("\n📚 Testing Knowledge Base...")
        kb_manager = KnowledgeBaseManager()
        
        if not kb_manager.knowledge_base:
            print("❌ Knowledge base is empty")
            print("   Run: python scripts/setup_knowledge_base.py")
            return False
        
        print(f"✅ Knowledge base loaded with {len(kb_manager.knowledge_base)} sources")
        for source in kb_manager.knowledge_base.keys():
            print(f"   - {source}")
        
        # Test context retrieval
        print("\n🔍 Testing Context Retrieval...")
        context = kb_manager.get_context("linkedin", "job posting")
        if context:
            print(f"✅ Context retrieved ({len(context)} characters)")
        else:
            print("❌ No context retrieved")
            return False
        
        # Test Claude service (if API key is valid)
        print("\n🤖 Testing Claude Service...")
        try:
            claude_service = ClaudeService(claude_key)
            
            # Test job posting generation
            test_job_data = {
                "job_title": "Senior Software Engineer",
                "platform": "linkedin",
                "location": "London, UK",
                "experience_level": "senior",
                "job_overview": "We're looking for a talented Senior Software Engineer to join our growing team.",
                "required_skills": "Python, React, PostgreSQL"
            }
            
            print("   Generating test job posting...")
            result = await claude_service.generate_job_posting(test_job_data)
            
            if result and result.get("success"):
                print("✅ Job posting generation successful!")
                print(f"   Model used: {result.get('model_used')}")
                print(f"   Content length: {len(result.get('content', ''))}")
                print(f"   Knowledge sources: {result.get('knowledge_sources', [])}")
            else:
                print("❌ Job posting generation failed")
                return False
                
        except Exception as e:
            if "authentication" in str(e).lower() or "api key" in str(e).lower():
                print("⚠️  Claude API authentication failed - check your API key")
                print(f"   Error: {e}")
                return False
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        
        print("\n🎉 All tests passed! Claude integration is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed:")
        print("   pip install anthropic sentence-transformers")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_job_posting_analysis():
    """Test the job posting analysis feature"""
    try:
        from services.claude_service import ClaudeService
        from core.config import settings
        
        claude_key = os.getenv('CLAUDE_API_KEY') or settings.CLAUDE_API_KEY
        if not claude_key:
            return False
        
        claude_service = ClaudeService(claude_key)
        
        test_content = """
        Senior Software Engineer - London
        
        We're looking for a Senior Software Engineer to join our team.
        
        Requirements:
        - 5+ years experience
        - Python, React
        - Good communication skills
        
        Apply now!
        """
        
        print("\n📊 Testing Job Posting Analysis...")
        result = await claude_service.analyze_job_posting(test_content)
        
        if result and result.get("success"):
            print("✅ Analysis successful!")
            print(f"   Score: {result.get('score')}/100")
            print(f"   Suggestions: {len(result.get('suggestions', []))}")
        else:
            print("❌ Analysis failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis test error: {e}")
        return False

if __name__ == "__main__":
    async def main():
        success = await test_claude_service()
        
        if success:
            await test_job_posting_analysis()
        
        print("\n" + "=" * 50)
        if success:
            print("🚀 Integration ready! You can now use the job posting generator.")
        else:
            print("🔧 Please fix the issues above before using the job posting generator.")
    
    asyncio.run(main())