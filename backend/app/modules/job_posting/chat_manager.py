import json
from pathlib import Path
from datetime import datetime
import os
import shutil

class ChatManager:
    def __init__(self):
        # Create necessary directories with absolute paths
        self.base_dir = Path(__file__).parent.parent / "data"
        self.data_dir = self.base_dir / "chats"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Main chat metadata file
        self.chats_file = self.base_dir / "chats_metadata.json"
        if not self.chats_file.exists():
            self.save_chats([])

        # Migrate old data if necessary
        self._migrate_old_data()

    def _migrate_old_data(self):
        """Migrate old data to the new structure if necessary"""
        old_chats_file = self.base_dir / "chats.json"
        if old_chats_file.exists():
            try:
                with open(old_chats_file, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                    if "chats" in old_data:
                        for chat in old_data["chats"]:
                            # Create a new directory for each chat
                            chat_dir = self.data_dir / str(chat["id"])
                            chat_dir.mkdir(exist_ok=True)
                            # Save metadata
                            with open(chat_dir / "metadata.json", "w", encoding="utf-8") as f:
                                json.dump({
                                    "id": chat["id"],
                                    "name": chat["name"],
                                    "created_at": chat.get("created_at", datetime.now().isoformat()),
                                    "updated_at": datetime.now().isoformat()
                                }, f, ensure_ascii=False, indent=2)
                            # Save chat history
                            if "messages" in chat:
                                with open(chat_dir / "history.json", "w", encoding="utf-8") as f:
                                    json.dump(chat["messages"], f, ensure_ascii=False, indent=2)
                # Rename the old file as backup
                old_chats_file.rename(old_chats_file.with_suffix('.json.bak'))
            except Exception as e:
                print(f"Error during migration: {e}")

    def load_chats(self):
        """Load the list of chats from their individual directories"""
        chats = []
        try:
            for chat_dir in sorted(self.data_dir.iterdir()):
                if chat_dir.is_dir():
                    metadata_file = chat_dir / "metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file, "r", encoding="utf-8") as f:
                            chat_data = json.load(f)
                            chats.append(chat_data)
            return sorted(chats, key=lambda x: x["id"])
        except Exception as e:
            print(f"Error loading chats: {e}")
            return []

    def save_chats(self, chats):
        """Save the list of chats to the main file"""
        try:
            with open(self.chats_file, "w", encoding="utf-8") as f:
                json.dump({"chats": chats}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving chats: {e}")

    def create_chat(self, name):
        """Create a new chat with its own directory"""
        chats = self.load_chats()
        new_id = max([chat.get("id", 0) for chat in chats], default=0) + 1
        
        chat_dir = self.data_dir / str(new_id)
        chat_dir.mkdir(exist_ok=True)
        
        new_chat = {
            "id": new_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save metadata
        with open(chat_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(new_chat, f, ensure_ascii=False, indent=2)
        
        # Create empty history file
        with open(chat_dir / "history.json", "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        
        return new_chat

    def rename_chat(self, chat_id: int, new_name: str):
        """Rename an existing chat"""
        chat_dir = self.data_dir / str(chat_id)
        if not chat_dir.exists():
            raise ValueError(f"Chat {chat_id} not found")
        
        metadata_file = chat_dir / "metadata.json"
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        metadata["name"] = new_name
        metadata["updated_at"] = datetime.now().isoformat()
        
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return metadata

    def delete_chat(self, chat_id: int):
        """Delete a chat and all its associated files"""
        chat_dir = self.data_dir / str(chat_id)
        if chat_dir.exists():
            shutil.rmtree(chat_dir)
        return {"status": "success", "message": f"Chat {chat_id} deleted"}

    def get_chat_history(self, chat_id: int):
        """Retrieve chat history"""
        chat_dir = self.data_dir / str(chat_id)
        history_file = chat_dir / "history.json"
        try:
            if history_file.exists():
                with open(history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading chat history for {chat_id}: {e}")
            return []

    def add_message(self, chat_id: int, sender: str, content: str):
        """Add a message to the chat history"""
        chat_dir = self.data_dir / str(chat_id)
        history_file = chat_dir / "history.json"
        
        try:
            history = self.get_chat_history(chat_id)
            new_message = {
                "sender": sender,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            history.append(new_message)
            
            # Update chat history file
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            # Update last modified timestamp in metadata
            metadata_file = chat_dir / "metadata.json"
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            metadata["updated_at"] = datetime.now().isoformat()
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
                
            return new_message
        except Exception as e:
            print(f"Error adding message to chat {chat_id}: {e}")
            raise

    def get_chat_list(self):
        """Retrieve the list of chats with their metadata"""
        return self.load_chats()