import json
import os
import time
from datetime import datetime
import uuid

class ChatHistoryManager:
    def __init__(self, history_dir="chat_histories"):
        self.history_dir = history_dir
        # Create the directory if it doesn't exist
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)

    def save_chat(self, history, chat_id=None):
        """Save a chat history to file"""
        if not chat_id:
            chat_id = str(uuid.uuid4())
        
        # Add timestamp for sorting - update timestamp if chat already exists
        timestamp = datetime.now().isoformat()
        
        # Check if chat already exists to preserve original timestamp
        original_timestamp = timestamp
        if os.path.exists(os.path.join(self.history_dir, f"{chat_id}.json")):
            try:
                with open(os.path.join(self.history_dir, f"{chat_id}.json"), "r") as f:
                    existing_data = json.load(f)
                    original_timestamp = existing_data.get("timestamp", timestamp)
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        
        # Create chat metadata
        chat_data = {
            "id": chat_id,
            "timestamp": original_timestamp,
            "last_updated": timestamp,
            "messages": history,
            # Extract first few user messages for preview
            "preview": self._generate_preview(history)
        }
        
        # Save to file
        with open(os.path.join(self.history_dir, f"{chat_id}.json"), "w") as f:
            json.dump(chat_data, f, indent=2)
        
        return chat_id
    
    def load_chat(self, chat_id):
        """Load a chat history from file"""
        try:
            with open(os.path.join(self.history_dir, f"{chat_id}.json"), "r") as f:
                chat_data = json.load(f)
                return chat_data["messages"]
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def get_chat_list(self, limit=10):
        """Get a list of recent chat sessions"""
        chats = []
        
        # Get all JSON files in the history directory
        try:
            files = [f for f in os.listdir(self.history_dir) if f.endswith('.json')]
        except FileNotFoundError:
            return []
            
        # Load each chat file and extract metadata
        for file in files:
            try:
                with open(os.path.join(self.history_dir, file), "r") as f:
                    chat_data = json.load(f)
                    chats.append({
                        "id": chat_data.get("id", file.replace(".json", "")),
                        "timestamp": chat_data.get("timestamp", ""),
                        "last_updated": chat_data.get("last_updated", ""),
                        "preview": chat_data.get("preview", "New chat")
                    })
            except (json.JSONDecodeError, KeyError):
                continue
                
        # Sort by last updated timestamp (newest first)
        chats.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
        
        # Return limited number
        return chats[:limit]
    
    def delete_chat(self, chat_id):
        """Delete a chat history file"""
        try:
            os.remove(os.path.join(self.history_dir, f"{chat_id}.json"))
            return True
        except FileNotFoundError:
            return False
    
    def _generate_preview(self, history):
        """Generate a preview text from the chat history"""
        # Find the first user message
        for msg in history:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                # Truncate long messages
                if len(content) > 40:
                    return content[:40] + "..."
                return content
        
        return "New chat"
    
    def test_functionality(self):
        """Test method to verify the ChatHistoryManager is working"""
        print("=== Testing Chat Manager ===")
        try:
            # Test saving a chat
            test_history = [{"role": "user", "content": "test message"}]
            chat_id = self.save_chat(test_history)
            print(f"Saved chat with ID: {chat_id}")
            
            # Test loading the chat
            loaded = self.load_chat(chat_id)
            print(f"Loaded chat: {loaded}")
            
            # Test getting chat list
            chats = self.get_chat_list()
            print(f"Chat list: {chats}")
            
            # Clean up test
            self.delete_chat(chat_id)
            print("Test chat deleted")
            
        except Exception as e:
            print(f"Error testing chat manager: {e}")
        print("=== End Test ===")