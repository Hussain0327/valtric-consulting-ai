"""
Session Management Routes for ValtricAI Consulting Agent
"""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from api.dependencies import get_current_user, get_project_id
from agent_logic.conversation_manager import conversation_manager
from models.schemas import ChatSession, ChatSessionCreate, ChatSessionUpdate, SessionStatus

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/sessions", response_model=List[ChatSession])
async def list_sessions(
    limit: int = Query(50, ge=1, le=100),
    status: Optional[SessionStatus] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    user = Depends(get_current_user)
):
    """List user's chat sessions with optional filtering"""
    try:
        sessions = await conversation_manager.list_user_sessions(
            user_id=user["id"], 
            limit=limit,
            status=status
        )
        
        # Apply date filtering if provided
        if from_date or to_date:
            filtered_sessions = []
            for session in sessions:
                session_date = session.created_at
                
                if from_date and session_date < from_date:
                    continue
                if to_date and session_date > to_date:
                    continue
                    
                filtered_sessions.append(session)
            sessions = filtered_sessions
        
        return sessions
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sessions")


@router.post("/sessions", response_model=ChatSession)
async def create_session(
    session_data: ChatSessionCreate,
    user = Depends(get_current_user),
    project_id = Depends(get_project_id)
):
    """Create a new chat session"""
    try:
        from uuid import uuid4
        session_id = str(uuid4())
        
        session = await conversation_manager.get_or_create_session(
            session_id=session_id,
            user_id=user["id"],
            project_id=project_id,
            persona=session_data.persona.value,
            framework=session_data.framework.value if session_data.framework else None
        )
        
        return session
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_session(
    session_id: str,
    user = Depends(get_current_user)
):
    """Get a specific session by ID"""
    try:
        session = await conversation_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify user has access to this session
        if session.user_id != user["id"]:
            raise HTTPException(status_code=403, detail="Access denied to this session")
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session")


@router.put("/sessions/{session_id}", response_model=ChatSession)
async def update_session(
    session_id: str,
    session_update: ChatSessionUpdate,
    user = Depends(get_current_user)
):
    """Update session title or status"""
    try:
        session = await conversation_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify user has access to this session
        if session.user_id != user["id"]:
            raise HTTPException(status_code=403, detail="Access denied to this session")
        
        # Update session fields
        if session_update.title is not None:
            session.title = session_update.title
        
        if session_update.status is not None:
            session.status = session_update.status
        
        # Update last activity
        session.last_activity = datetime.utcnow()
        
        # Save changes
        success = await conversation_manager._update_session_in_db(session)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update session")
        
        # Update cache
        conversation_manager.active_sessions[session_id] = session
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update session")


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user = Depends(get_current_user)
):
    """Delete a session and all its messages"""
    try:
        success = await conversation_manager.delete_session(session_id, user["id"])
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found or access denied")
        
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")


@router.get("/sessions/stats/summary")
async def get_session_stats(
    user = Depends(get_current_user)
):
    """Get session analytics and statistics for the user"""
    try:
        # Get all sessions for the user
        all_sessions = await conversation_manager.list_user_sessions(user["id"], limit=1000)
        
        # Calculate statistics
        total_sessions = len(all_sessions)
        active_sessions = sum(1 for s in all_sessions if s.status == SessionStatus.ACTIVE)
        archived_sessions = sum(1 for s in all_sessions if s.status == SessionStatus.ARCHIVED)
        total_messages = sum(s.message_count for s in all_sessions)
        
        # Group by persona
        persona_stats = {}
        for session in all_sessions:
            persona = session.persona
            if persona not in persona_stats:
                persona_stats[persona] = {"count": 0, "messages": 0}
            persona_stats[persona]["count"] += 1
            persona_stats[persona]["messages"] += session.message_count
        
        # Group by framework
        framework_stats = {}
        for session in all_sessions:
            framework = session.framework or "general"
            if framework not in framework_stats:
                framework_stats[framework] = {"count": 0, "messages": 0}
            framework_stats[framework]["count"] += 1
            framework_stats[framework]["messages"] += session.message_count
        
        # Recent activity (last 7 days)
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_sessions = [s for s in all_sessions if s.last_activity >= seven_days_ago]
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "archived_sessions": archived_sessions,
            "total_messages": total_messages,
            "average_messages_per_session": total_messages / total_sessions if total_sessions > 0 else 0,
            "recent_sessions_count": len(recent_sessions),
            "persona_breakdown": persona_stats,
            "framework_breakdown": framework_stats
        }
    except Exception as e:
        logger.error(f"Failed to get session stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session statistics")