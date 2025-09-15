"""
Conversation Manager for ValtricAI Consulting Agent

Handles session management, conversation history, and context preservation
for multi-turn consulting conversations with proper Supabase integration.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from uuid import uuid4

from config.settings import settings, RAGMode
from rag_system.supabase_client import supabase_manager
from rag_system.retriever import hybrid_retriever
from models.schemas import ChatMessage, SessionStatus, MessageRole

logger = logging.getLogger(__name__)


@dataclass
class ConversationSession:
    """Represents a conversation session"""
    session_id: str
    user_id: str  
    project_id: str
    title: str
    persona: str = "partner"
    framework: Optional[str] = None
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = None
    last_activity: datetime = None
    message_count: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.last_activity is None:
            self.last_activity = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages for context - implementation depends on storage"""
        # This will be implemented with actual message retrieval
        return []

    def get_messages(
        self, 
        limit: int = 50, 
        before_timestamp: Optional[datetime] = None
    ) -> List[ChatMessage]:
        """Get messages with pagination - implementation depends on storage"""
        return []


class ConversationManager:
    """Manages conversation sessions and message history"""
    
    def __init__(self):
        self.active_sessions: Dict[str, ConversationSession] = {}
        self.session_timeout = timedelta(hours=24)  # Sessions expire after 24 hours
        
    async def get_or_create_session(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        persona: str = "partner",
        framework: Optional[str] = None
    ) -> ConversationSession:
        """Get existing session or create new one"""
        
        try:
            # Try to get from cache first
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.last_activity = datetime.utcnow()
                return session
            
            # Try to load from database
            session = await self._load_session_from_db(session_id)
            
            if session:
                # Verify user has access
                if session.user_id != user_id:
                    raise PermissionError(f"User {user_id} cannot access session {session_id}")
                
                # Update activity and cache
                session.last_activity = datetime.utcnow()
                self.active_sessions[session_id] = session
                
                # Update in database
                await self._update_session_in_db(session)
                
                return session
            
            # Create new session
            return await self._create_new_session(
                session_id, user_id, project_id, persona, framework
            )
            
        except Exception as e:
            logger.error(f"Failed to get/create session {session_id}: {e}")
            raise

    async def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get session by ID"""
        
        try:
            # Check cache first
            if session_id in self.active_sessions:
                return self.active_sessions[session_id]
            
            # Load from database
            return await self._load_session_from_db(session_id)
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    async def add_message(
        self,
        session_id: str,
        user_message: str,
        ai_response: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Add conversation turn to session"""
        
        try:
            # Get session
            session = await self.get_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return False
            
            # Store messages in database
            await self._store_messages(
                session_id=session_id,
                user_message=user_message,
                ai_response=ai_response,
                metadata=metadata or {}
            )
            
            # Update session
            session.message_count += 2  # User + AI message
            session.last_activity = datetime.utcnow()
            
            # Update session in database and cache
            await self._update_session_in_db(session)
            self.active_sessions[session_id] = session
            
            logger.info(f"Added conversation turn to session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add message to session {session_id}: {e}")
            return False

    async def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a session and its messages"""
        
        try:
            # Get session and verify ownership
            session = await self.get_session(session_id)
            if not session:
                return False
                
            if session.user_id != user_id:
                logger.warning(f"User {user_id} attempted to delete session {session_id} owned by {session.user_id}")
                return False
            
            # Delete from database
            success = await self._delete_session_from_db(session_id)
            
            # Remove from cache
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            logger.info(f"Deleted session {session_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

    async def list_user_sessions(
        self, 
        user_id: str, 
        limit: int = 50,
        status: Optional[SessionStatus] = None
    ) -> List[ConversationSession]:
        """List sessions for a user"""
        
        try:
            # Query sessions from tenant database
            query = supabase_manager.tenant_client.table("chat_sessions").select("*")
            query = query.eq("user_id", user_id).order("last_activity", desc=True).limit(limit)
            
            if status:
                query = query.eq("status", status.value)
            
            result = query.execute()
            
            sessions = []
            for row in result.data or []:
                session = ConversationSession(
                    session_id=row["id"],
                    user_id=row["user_id"],
                    project_id=row["project_id"],
                    title=row["title"],
                    persona=row.get("persona", "partner"),
                    framework=row.get("framework"),
                    status=SessionStatus(row.get("status", "active")),
                    created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                    last_activity=datetime.fromisoformat(row["last_activity"].replace("Z", "+00:00")),
                    message_count=row.get("message_count", 0),
                    metadata=row.get("metadata", {})
                )
                sessions.append(session)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to list sessions for user {user_id}: {e}")
            return []

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions from cache and database"""
        
        try:
            expired_count = 0
            current_time = datetime.utcnow()
            
            # Clean up cache
            expired_sessions = []
            for session_id, session in self.active_sessions.items():
                if current_time - session.last_activity > self.session_timeout:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
                expired_count += 1
            
            # Mark expired sessions in database
            cutoff_time = current_time - self.session_timeout
            
            result = supabase_manager.tenant_admin_client.table("chat_sessions").update({
                "status": SessionStatus.ARCHIVED.value
            }).lt("last_activity", cutoff_time.isoformat()).eq("status", SessionStatus.ACTIVE.value).execute()
            
            if result.data:
                expired_count += len(result.data)
            
            logger.info(f"Cleaned up {expired_count} expired sessions")
            return expired_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0

    async def _create_new_session(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        persona: str,
        framework: Optional[str]
    ) -> ConversationSession:
        """Create a new conversation session"""
        
        try:
            # Generate title based on persona and framework
            title = self._generate_session_title(persona, framework)
            
            session = ConversationSession(
                session_id=session_id,
                user_id=user_id,
                project_id=project_id,
                title=title,
                persona=persona,
                framework=framework,
                status=SessionStatus.ACTIVE,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                message_count=0,
                metadata={}
            )
            
            # Store in database
            await self._store_session_in_db(session)
            
            # Cache it
            self.active_sessions[session_id] = session
            
            logger.info(f"Created new session {session_id} for user {user_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            raise

    async def _store_session_in_db(self, session: ConversationSession) -> bool:
        """Store session in Supabase"""
        
        try:
            data = {
                "id": session.session_id,
                "user_id": session.user_id,
                "project_id": session.project_id,
                "title": session.title,
                "persona": session.persona,
                "framework": session.framework,
                "status": session.status.value,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "message_count": session.message_count,
                "metadata": session.metadata
            }
            
            result = supabase_manager.tenant_admin_client.table("chat_sessions").insert(data).execute()
            
            if result.data:
                logger.debug(f"Stored session {session.session_id} in database")
                return True
            else:
                logger.error(f"Failed to store session {session.session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Database error storing session {session.session_id}: {e}")
            return False

    async def _load_session_from_db(self, session_id: str) -> Optional[ConversationSession]:
        """Load session from Supabase"""
        
        try:
            result = supabase_manager.tenant_client.table("chat_sessions").select("*").eq("id", session_id).execute()
            
            if not result.data:
                return None
            
            row = result.data[0]
            
            session = ConversationSession(
                session_id=row["id"],
                user_id=row["user_id"],
                project_id=row["project_id"],
                title=row["title"],
                persona=row.get("persona", "partner"),
                framework=row.get("framework"),
                status=SessionStatus(row.get("status", "active")),
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                last_activity=datetime.fromisoformat(row["last_activity"].replace("Z", "+00:00")),
                message_count=row.get("message_count", 0),
                metadata=row.get("metadata", {})
            )
            
            logger.debug(f"Loaded session {session_id} from database")
            return session
            
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None

    async def _update_session_in_db(self, session: ConversationSession) -> bool:
        """Update session in database"""
        
        try:
            data = {
                "last_activity": session.last_activity.isoformat(),
                "message_count": session.message_count,
                "status": session.status.value,
                "metadata": session.metadata
            }
            
            result = supabase_manager.tenant_admin_client.table("chat_sessions").update(data).eq("id", session.session_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Failed to update session {session.session_id}: {e}")
            return False

    async def _delete_session_from_db(self, session_id: str) -> bool:
        """Delete session and messages from database"""
        
        try:
            # Delete messages first
            supabase_manager.tenant_admin_client.table("chat_messages").delete().eq("session_id", session_id).execute()
            
            # Delete session
            result = supabase_manager.tenant_admin_client.table("chat_sessions").delete().eq("id", session_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

    async def _store_messages(
        self,
        session_id: str,
        user_message: str,
        ai_response: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Store user and AI messages in database"""
        
        try:
            current_time = datetime.utcnow().isoformat()
            
            messages = [
                {
                    "id": str(uuid4()),
                    "session_id": session_id,
                    "role": MessageRole.USER.value,
                    "content": user_message,
                    "timestamp": current_time,
                    "metadata": {}
                },
                {
                    "id": str(uuid4()),
                    "session_id": session_id,
                    "role": MessageRole.ASSISTANT.value,
                    "content": ai_response,
                    "timestamp": current_time,
                    "metadata": metadata
                }
            ]
            
            result = supabase_manager.tenant_admin_client.table("chat_messages").insert(messages).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Failed to store messages for session {session_id}: {e}")
            return False

    async def get_framework_context(self, query: str, k: int = 3) -> str:
        """Retrieve framework context for conversation flows"""
        try:
            retrieval = await hybrid_retriever.retrieve(
                query=query,
                k=k,
                mode=RAGMode.GLOBAL
            )
            
            if retrieval.results:
                logger.info(f"Retrieved {len(retrieval.results)} framework documents for conversation")
                return retrieval.context_text
            
            return ""
            
        except Exception as e:
            logger.warning(f"Framework context retrieval failed: {e}")
            return ""

    def _generate_session_title(self, persona: str, framework: Optional[str]) -> str:
        """Generate a descriptive session title"""
        
        persona_names = {
            "associate": "Associate Consultation",
            "partner": "Partner Consultation", 
            "senior_partner": "Senior Partner Consultation"
        }
        
        framework_names = {
            "swot": "SWOT Analysis",
            "porters": "Porter's 5 Forces",
            "mckinsey": "McKinsey 7S"
        }
        
        base_title = persona_names.get(persona, "Business Consultation")
        
        if framework:
            framework_name = framework_names.get(framework, framework.title())
            return f"{base_title} - {framework_name}"
        
        return base_title


# Global conversation manager instance
conversation_manager = ConversationManager()