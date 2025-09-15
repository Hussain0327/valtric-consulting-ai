"""
Enhanced Conversation Manager with Profile Memory
Handles conversation persistence, profile memory, and deterministic recall using dual Supabase setup.
"""

import logging
import uuid
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from config.supabase_clients import get_tenant_client

logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    """Represents a single conversation message"""
    id: str
    session_id: str
    role: str  # "user" | "assistant" | "system"
    content: str
    model_used: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProfileMemory:
    """Represents stored profile information"""
    key: str
    value: str
    confidence: float
    updated_at: datetime

class EnhancedConversationManager:
    """Conversation manager with profile memory and dual Supabase support"""
    
    def __init__(self):
        self.tenant = None
        
    def _get_tenant(self):
        """Lazy load tenant client"""
        if self.tenant is None:
            from config.settings import settings
            from supabase import create_client
            self.tenant = create_client(
                settings.tenant_supabase_url,
                settings.tenant_supabase_service_role_key
            )
        return self.tenant
    
    async def create_session(self, user_id: str, project_id: str = "default") -> str:
        """Create a new conversation session"""
        try:
            session_id = str(uuid.uuid4())
            
            # Create session in tenant DB
            result = self._get_tenant().table("chat_sessions").insert({
                "id": session_id,
                "user_id": user_id,
                "project_id": project_id,
                "title": f"Chat {datetime.now().strftime('%m/%d %H:%M')}",
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {}
            }).execute()
            
            logger.info(f"Created session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    async def save_message(
        self, 
        session_id: str, 
        role: str, 
        content: str, 
        model_used: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Save a message to the conversation"""
        try:
            message_data = {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "role": role,
                "content": content,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            if model_used:
                message_data["model_used"] = model_used
            
            self._get_tenant().table("chat_messages").insert(message_data).execute()
            logger.debug(f"Saved {role} message to session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            raise
    
    async def load_conversation(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Load conversation history"""
        try:
            result = self._get_tenant().table("chat_messages")\
                .select("*")\
                .eq("session_id", session_id)\
                .order("created_at", desc=False)\
                .limit(limit)\
                .execute()
            
            messages = []
            for msg in result.data or []:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                    "model_used": msg.get("model_used"),
                    "created_at": msg.get("created_at"),
                    "metadata": msg.get("metadata", {})
                })
            
            logger.debug(f"Loaded {len(messages)} messages for session {session_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Failed to load conversation: {e}")
            return []
    
    def last_user_message(self, history: List[Dict[str, Any]]) -> Optional[str]:
        """Get the last user message from history (excluding current)"""
        user_messages = [msg for msg in history if msg.get("role") == "user"]
        if len(user_messages) >= 2:  # Current + previous
            return user_messages[-2].get("content", "").strip()
        elif len(user_messages) == 1:
            return user_messages[0].get("content", "").strip()
        return None
    
    async def upsert_profile(
        self, 
        session_id: str, 
        key: str, 
        value: str, 
        confidence: float = 0.9
    ):
        """Store or update profile memory"""
        try:
            self._get_tenant().table("assistant_profile_memory").upsert({
                "session_id": session_id,
                "key": key,
                "value": value,
                "confidence": confidence,
                "updated_at": datetime.utcnow().isoformat()
            }, on_conflict=["session_id", "key"]).execute()
            
            logger.info(f"Saved profile memory: {key}={value} for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to save profile memory: {e}")
            raise
    
    async def get_profile(self, session_id: str, key: str) -> Optional[str]:
        """Get stored profile memory value"""
        try:
            result = self._get_tenant().table("assistant_profile_memory")\
                .select("value")\
                .eq("session_id", session_id)\
                .eq("key", key)\
                .single()\
                .execute()
            
            return result.data.get("value") if result.data else None
            
        except Exception as e:
            logger.debug(f"Profile key '{key}' not found for session {session_id}")
            return None
    
    async def get_all_profile_data(self, session_id: str) -> Dict[str, str]:
        """Get all profile data for a session"""
        try:
            result = self._get_tenant().table("assistant_profile_memory")\
                .select("key, value")\
                .eq("session_id", session_id)\
                .execute()
            
            profile = {}
            for item in result.data or []:
                profile[item["key"]] = item["value"]
                
            return profile
            
        except Exception as e:
            logger.error(f"Failed to get profile data: {e}")
            return {}
    
    async def set_sticky_routing(self, session_id: str, turns: int = 3):
        """Set sticky routing for finance threads"""
        try:
            # Update session metadata with sticky routing
            result = self._get_tenant().table("chat_sessions")\
                .select("metadata")\
                .eq("id", session_id)\
                .single()\
                .execute()
            
            metadata = result.data.get("metadata", {}) if result.data else {}
            metadata["sticky_reasoning_turns"] = turns
            
            self._get_tenant().table("chat_sessions")\
                .update({"metadata": metadata})\
                .eq("id", session_id)\
                .execute()
            
            logger.info(f"Set sticky routing for {turns} turns on session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to set sticky routing: {e}")
    
    async def consume_sticky_routing(self, session_id: str) -> bool:
        """Check and consume sticky routing turn"""
        try:
            result = self._get_tenant().table("chat_sessions")\
                .select("metadata")\
                .eq("id", session_id)\
                .single()\
                .execute()
            
            if not result.data:
                return False
                
            metadata = result.data.get("metadata", {})
            sticky_turns = metadata.get("sticky_reasoning_turns", 0)
            
            if sticky_turns > 0:
                # Consume one turn
                metadata["sticky_reasoning_turns"] = sticky_turns - 1
                self._get_tenant().table("chat_sessions")\
                    .update({"metadata": metadata})\
                    .eq("id", session_id)\
                    .execute()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to consume sticky routing: {e}")
            return False
    
    def meta_reply(self, conversation_id: str, content: str, model: str = "server-meta"):
        """Create a meta reply response"""
        # Save the meta response to conversation
        asyncio.create_task(self.save_message(
            conversation_id, 
            "assistant", 
            content, 
            model_used=model
        ))
        
        return {
            "message": content,
            "model_used": model,
            "complexity_score": 0.0,
            "conversation_id": conversation_id,
            "routing_signals": ["meta"]
        }

# Global instance
enhanced_conversation_manager = EnhancedConversationManager()