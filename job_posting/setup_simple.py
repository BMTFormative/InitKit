#!/usr/bin/env python3
"""
Simple setup script that doesn't require complex dependencies.
"""
import os
import json
import shutil
from pathlib import Path

def setup_simple():
    """Setup the project with minimal dependencies"""
    
    print("=== Claude Job Posting Simple Setup ===\n")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file from template...")
        shutil.copy(".env.example", ".env")
        print("✅ .env file created")
        print("⚠️  Please edit .env and add your ANTHROPIC_API_KEY")
    else:
        print("✅ .env file already exists")
    
    # Create necessary directories
    dirs_to_create = [
        "data/chats",
        "data/knowledge_base", 
        "data/vector_store"
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")
    
    # Copy knowledge base files if they exist
    source_kb = Path("../KB")
    target_kb = Path("data/knowledge_base")
    
    if source_kb.exists():
        print(f"\n📁 Copying KB files from {source_kb}...")
        copied = 0
        for txt_file in source_kb.glob("*.txt"):
            dest_file = target_kb / txt_file.name
            shutil.copy2(txt_file, dest_file)
            print(f"   Copied: {txt_file.name}")
            copied += 1
        
        if copied > 0:
            print(f"✅ Copied {copied} KB files successfully")
        else:
            print("⚠️  No .txt files found in KB directory")
    else:
        print(f"⚠️  KB directory not found: {source_kb}")
        print("   Please create your knowledge base files manually in data/knowledge_base/")
    
    # Create default user preferences
    user_prefs = Path("data/user_prefs.json")
    if not user_prefs.exists():
        default_prefs = {
            "company_name": "Vodafone",
            "industry": "Telecom", 
            "location": "London",
            "about_company": ""
        }
        
        with open(user_prefs, 'w', encoding='utf-8') as f:
            json.dump(default_prefs, f, indent=2, ensure_ascii=False)
        print("✅ Created default user preferences")
    
    # Create empty chat metadata
    chat_metadata = Path("data/chats_metadata.json")
    if not chat_metadata.exists():
        with open(chat_metadata, 'w', encoding='utf-8') as f:
            json.dump({"chats": []}, f, indent=2)
        print("✅ Created chat metadata file")
    
    print("\n🎉 Simple setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file and add your ANTHROPIC_API_KEY=sk-ant-your-key-here")
    print("2. Install basic dependencies: pip install fastapi uvicorn anthropic python-dotenv")
    print("3. Run: python test_simple.py (to test)")
    print("4. Run: uvicorn main:app --reload --port 8001")
    print("5. Open: http://127.0.0.1:8001")

if __name__ == "__main__":
    setup_simple()