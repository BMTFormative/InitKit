#!/usr/bin/env python3
"""
Test script to verify Claude setup and knowledge base functionality.
"""
import sys
from pathlib import Path
import asyncio

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from src.claude_api import ClaudeAPI
from src.knowledge_base import KnowledgeBaseManager
from config.settings import AVAILABLE_MODELS, DEFAULT_MODEL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_claude_setup():
    """Test Claude API and knowledge base setup"""
    
    print("=== Claude Job Posting Setup Test ===\n")
    
    # Test 1: Claude API Connection
    print("1. Testing Claude API Connection...")
    try:
        claude_api = ClaudeAPI()
        
        test_message = "Hello! Can you confirm you're working correctly?"
        response = await claude_api.send_message(test_message)
        
        if response:
            print("✅ Claude API connection successful")
            print(f"   Response length: {len(response)} characters")
            print(f"   Preview: {response[:100]}...")
        else:
            print("❌ No response from Claude API")
            return False
            
    except Exception as e:
        print(f"❌ Claude API connection failed: {e}")
        return False
    
    print("\n" + "="*50)
    
    # Test 2: Knowledge Base
    print("\n2. Testing Knowledge Base...")
    try:
        kb_manager = KnowledgeBaseManager()
        
        # Get KB stats
        stats = kb_manager.get_stats()
        print(f"✅ Knowledge base loaded")
        print(f"   Files: {stats.get('kb_files_count', 0)}")
        print(f"   Vector documents: {stats.get('vector_documents', 0)}")
        print(f"   Files found: {stats.get('kb_files', [])}")
        
        if stats.get('vector_documents', 0) == 0:
            print("⚠️  No documents in vector store. Run setup_kb.py first.")
            return False
            
    except Exception as e:
        print(f"❌ Knowledge base error: {e}")
        return False
    
    print("\n" + "="*50)
    
    # Test 3: Knowledge Base Search
    print("\n3. Testing Knowledge Base Search...")
    try:
        # Test LinkedIn-specific search
        linkedin_context = kb_manager.search_knowledge_base("LinkedIn job posting format", "linkedin")
        
        if linkedin_context:
            print("✅ LinkedIn knowledge base search successful")
            print(f"   Context length: {len(linkedin_context)} characters")
            print(f"   Preview: {linkedin_context[:200]}...")
        else:
            print("⚠️  No LinkedIn context found in knowledge base")
        
        # Test general search
        general_context = kb_manager.search_knowledge_base("job posting structure")
        
        if general_context:
            print("✅ General knowledge base search successful")
            print(f"   Context length: {len(general_context)} characters")
        else:
            print("⚠️  No general context found in knowledge base")
            
    except Exception as e:
        print(f"❌ Knowledge base search error: {e}")
        return False
    
    print("\n" + "="*50)
    
    # Test 4: End-to-End Job Posting Generation
    print("\n4. Testing Job Posting Generation...")
    try:
        # Test LinkedIn job posting with knowledge base
        job_request = """Create a LinkedIn job posting for a Software Engineer position.
Company: TestCorp
Industry: Technology
Location: Remote
Use LinkedIn-specific formatting with emojis and bullet points."""
        
        print(f"Request: {job_request[:100]}...")
        
        # Search for relevant context
        context = kb_manager.search_knowledge_base(job_request, "linkedin")
        print(f"   Found context: {len(context)} characters")
        
        # Generate response
        response = await claude_api.send_message(job_request, context)
        
        if response:
            print("✅ Job posting generation successful")
            print(f"   Response length: {len(response)} characters")
            
            # Check for LinkedIn-specific formatting
            if any(emoji in response for emoji in ["🔹", "✅", "💼", "🚀"]):
                print("✅ Response includes LinkedIn-style emojis")
            
            if "bullet" in response.lower() or "•" in response:
                print("✅ Response includes bullet points")
                
            print(f"\n   Preview:\n{response[:400]}...")
            
        else:
            print("❌ No response from job posting generation")
            return False
            
    except Exception as e:
        print(f"❌ Job posting generation error: {e}")
        return False
    
    print("\n" + "="*70)
    print("🎉 All tests completed successfully!")
    print("\nYour Claude Job Posting system is ready to use!")
    print("\nTo start the application:")
    print("  uvicorn main:app --reload --port 8001")
    print("  Open: http://127.0.0.1:8001")
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_claude_setup())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()