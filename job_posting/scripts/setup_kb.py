#!/usr/bin/env python3
"""
Setup script to initialize the knowledge base from source files.
Run this after setting up your .env file.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from src.knowledge_base import KnowledgeBaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_knowledge_base():
    """Initialize the knowledge base from source files"""
    
    print("=== Claude Job Posting KB Setup ===\n")
    
    try:
        # Initialize KB manager
        kb_manager = KnowledgeBaseManager()
        
        # Path to your KB files (adjust as needed)
        source_kb_path = "../KB"  # Relative to current directory
        source_kb_full_path = Path(__file__).parent.parent.parent / "KB"
        
        print(f"Looking for KB files in: {source_kb_full_path}")
        
        # Check if source KB directory exists
        if source_kb_full_path.exists():
            print(f"✅ Found KB directory: {source_kb_full_path}")
            
            # List available files
            txt_files = list(source_kb_full_path.glob("*.txt"))
            print(f"Found {len(txt_files)} text files:")
            for file in txt_files:
                print(f"  - {file.name}")
            
            # Copy files to project KB directory
            print("\n📁 Copying KB files...")
            success = kb_manager.copy_kb_files_from_source(str(source_kb_full_path))
            
            if success:
                print("✅ KB files copied successfully")
                
                # Load into vector store
                print("\n🔄 Loading KB into vector store...")
                load_success = kb_manager.load_knowledge_base()
                
                if load_success:
                    print("✅ Knowledge base loaded successfully")
                    
                    # Show stats
                    print("\n📊 Knowledge Base Statistics:")
                    stats = kb_manager.get_stats()
                    print(f"  - Files: {stats.get('kb_files_count', 0)}")
                    print(f"  - Vector documents: {stats.get('vector_documents', 0)}")
                    print(f"  - Embedding model: {stats.get('embedding_model', 'Unknown')}")
                    
                    print("\n🎉 Setup completed successfully!")
                    print("\nNext steps:")
                    print("1. Set your ANTHROPIC_API_KEY in .env file")
                    print("2. Run: uvicorn main:app --reload --port 8001")
                    print("3. Open: http://127.0.0.1:8001")
                    
                    return True
                else:
                    print("❌ Failed to load knowledge base into vector store")
                    return False
            else:
                print("❌ Failed to copy KB files")
                return False
        else:
            print(f"❌ KB directory not found: {source_kb_full_path}")
            print("\nPlease ensure you have created the KB directory with your knowledge base files:")
            print("  - Crafting Compelling LinkedIn Job Posts.txt")
            print("  - KB2.txt")
            return False
            
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    setup_knowledge_base()