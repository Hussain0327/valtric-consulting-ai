"""
Chat API Routes for ValtricAI Consulting Agent

Handles real-time chat interactions with AI consultants, including:
- Streaming responses via WebSocket
- Context-aware conversations with RAG
- Multi-persona consultant selection
- Session management
"""

import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from config.settings import settings, RAGMode
from rag_system.retriever import hybrid_retriever
from rag_system.supabase_client import supabase_manager
from agent_logic.model_router import model_router
from agent_logic.conversation_manager import conversation_manager
from agent_logic.data_generator import data_generator
from services.queue_service import queue_service
from api.dependencies import get_current_user, get_project_id
from models.schemas import ChatMessage, ChatResponse, StreamingChatResponse, RetrievalSource

logger = logging.getLogger(__name__)

router = APIRouter()

# =============================================================================
# Request/Response Models
# =============================================================================

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    persona: Optional[str] = Field("partner", description="AI consultant persona (associate/partner/senior_partner)")
    framework: Optional[str] = Field(None, description="Specific framework to use (swot/porters/mckinsey)")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    streaming: bool = Field(True, description="Enable streaming response")

class ChatHistoryRequest(BaseModel):
    """Chat history request model"""
    session_id: str = Field(..., description="Session ID")
    limit: Optional[int] = Field(50, ge=1, le=100, description="Maximum number of messages")
    before_timestamp: Optional[datetime] = Field(None, description="Get messages before this timestamp")

# =============================================================================
# Chat Endpoints
# =============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user),
    project_id = Depends(get_project_id)
):
    """
    Send a message to the AI consultant (non-streaming)
    
    This endpoint provides a complete response after processing.
    For real-time streaming, use the WebSocket endpoint.
    """
    try:
        session_id = request.session_id or str(uuid4())
        
        # Get or create conversation session
        conversation = await conversation_manager.get_or_create_session(
            session_id=session_id,
            user_id=user["id"],
            project_id=project_id
        )
        
        # Retrieve relevant context using RAG
        retrieval_context = await hybrid_retriever.retrieve(
            query=request.message,
            project_id=project_id,
            k=8
        )
        
        # Generate AI response
        model_response = await model_router.generate_response(
            message=request.message,
            persona=request.persona,
            context=retrieval_context.context_text,
            conversation_history=conversation.get_recent_messages(),
            framework=request.framework
        )

        # Process AI response for structured data
        data_result = data_generator.process_ai_response(model_response.content)

        # Map retrieval results to response schema
        top_sources: List[RetrievalSource] = []
        for result in retrieval_context.results[:5]:
            snippet = result.text[:200] + "..." if len(result.text) > 200 else result.text
            top_sources.append(
                RetrievalSource(
                    id=result.id or "unknown",
                    text=snippet,
                    similarity_score=result.similarity_score,
                    source_type=result.source_type,
                    source_label=result.source_label,
                    metadata=result.metadata
                )
            )
        
        # Queue export generation if structured data is available
        export_urls = {}
        if data_result['exportable'] and data_result['structured_data']:
            try:
                # Queue export generation instead of blocking
                export_job = await queue_service.enqueue_export_job(
                    session_id=session_id,
                    structured_data=data_result['structured_data'],
                    export_types=['excel', 'pdf', 'powerpoint']
                )
                
                # Return status URLs instead of direct download URLs
                export_urls = {
                    'status': export_job['status'],
                    'job_id': export_job['job_id'],
                    'status_url': export_job.get('status_url'),
                    'message': 'Export generation queued - check status URL for progress'
                }
                
                logger.info(f"Queued exports for session {session_id}: job {export_job['job_id']}")
            except Exception as e:
                logger.error(f"Export queueing failed: {e}")
                export_urls = {
                    'status': 'failed',
                    'message': 'Failed to queue export generation'
                }
        
        # Save conversation turn
        background_tasks.add_task(
            conversation_manager.add_message,
            session_id=session_id,
            user_message=request.message,
            ai_response=model_response.content,
            metadata={
                "persona": request.persona,
                "framework": request.framework,
                "context_sources": len(retrieval_context.results),
                "model_used": model_response.model_used,
                "tokens_used": model_response.usage,
                "data_type": data_result['data_type'],
                "exportable": data_result['exportable']
            }
        )

        return ChatResponse(
            session_id=session_id,
            message=model_response.content,
            persona=request.persona,
            framework=request.framework,
            sources=top_sources,
            metadata={
                "model": model_response.model_used,
                "usage": model_response.usage,
                "context_quality": retrieval_context.metadata
            },
            # New structured data fields
            data_type=data_result['data_type'],
            structured_data=data_result['structured_data'],
            chart_config=data_result['chart_config'],
            export_urls=export_urls if export_urls else None,
            has_attachments=bool(export_urls),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Chat message failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.post("/chat/stream")
async def stream_chat_message(
    request: ChatRequest,
    user = Depends(get_current_user),
    project_id = Depends(get_project_id)
):
    """
    Stream AI consultant response (Server-Sent Events)
    
    Returns a streaming response with incremental message parts.
    """
    try:
        session_id = request.session_id or str(uuid4())
        
        # Get conversation context
        conversation = await conversation_manager.get_or_create_session(
            session_id=session_id,
            user_id=user["id"], 
            project_id=project_id
        )
        
        # Retrieve RAG context
        retrieval_context = await hybrid_retriever.retrieve(
            query=request.message,
            project_id=project_id,
            k=8
        )
        
        async def generate_stream():
            """Generate streaming response"""
            try:
                # Send initial context
                yield f"data: {json.dumps({'type': 'context', 'sources': len(retrieval_context.results)})}\n\n"
                
                # Stream AI response
                full_response = ""
                async for chunk in model_router.stream_response(
                    message=request.message,
                    persona=request.persona,
                    context=retrieval_context.context_text,
                    conversation_history=conversation.get_recent_messages(),
                    framework=request.framework
                ):
                    full_response += chunk.get("content", "")
                    
                    # Send chunk
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk.get('content', '')})}\n\n"
                
                # Send completion
                yield f"data: {json.dumps({'type': 'complete', 'session_id': session_id})}\n\n"
                
                # Save conversation (async)
                await conversation_manager.add_message(
                    session_id=session_id,
                    user_message=request.message,
                    ai_response=full_response,
                    metadata={
                        "persona": request.persona,
                        "framework": request.framework,
                        "streaming": True
                    }
                )
                
            except Exception as e:
                logger.error(f"Streaming failed: {e}")
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
        
    except Exception as e:
        logger.error(f"Stream setup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Streaming setup failed: {str(e)}")

# =============================================================================
# WebSocket Chat
# =============================================================================

@router.websocket("/chat/ws")
async def websocket_chat(
    websocket: WebSocket,
    project_id: str,
    session_id: Optional[str] = None
):
    """
    Real-time WebSocket chat with AI consultant
    
    Supports bidirectional communication with streaming responses.
    """
    await websocket.accept()
    session_id = session_id or str(uuid4())
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "chat":
                await handle_websocket_chat(websocket, data, session_id, project_id)
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                await websocket.send_json({
                    "type": "error",
                    "error": f"Unknown message type: {message_type}"
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({
            "type": "error", 
            "error": str(e)
        })

async def handle_websocket_chat(
    websocket: WebSocket,
    data: Dict[str, Any],
    session_id: str,
    project_id: str
):
    """Handle WebSocket chat message"""
    try:
        message = data.get("message", "")
        persona = data.get("persona", "partner") 
        framework = data.get("framework")
        
        if not message.strip():
            await websocket.send_json({
                "type": "error",
                "error": "Message cannot be empty"
            })
            return
        
        # Get conversation context (simplified for WebSocket)
        # In production, you'd want to authenticate the WebSocket connection
        
        # Retrieve RAG context
        retrieval_context = await hybrid_retriever.retrieve(
            query=message,
            project_id=project_id,
            k=6
        )
        
        # Send sources first
        await websocket.send_json({
            "type": "sources",
            "sources": [
                {
                    "text": r.text[:200] + "..." if len(r.text) > 200 else r.text,
                    "source_label": r.source_label,
                    "similarity": r.similarity_score
                }
                for r in retrieval_context.results[:3]
            ]
        })
        
        # Stream response
        full_response = ""
        async for chunk in model_router.stream_response(
            message=message,
            persona=persona,
            context=retrieval_context.context_text,
            conversation_history=[],  # Simplified for demo
            framework=framework
        ):
            content = chunk.get("content", "")
            full_response += content
            
            await websocket.send_json({
                "type": "content",
                "content": content
            })
        
        # Send completion
        await websocket.send_json({
            "type": "complete",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"WebSocket chat handling failed: {e}")
        await websocket.send_json({
            "type": "error",
            "error": str(e)
        })

# =============================================================================
# Chat History
# =============================================================================

@router.post("/chat/history", response_model=List[ChatMessage])
async def get_chat_history(
    request: ChatHistoryRequest,
    user = Depends(get_current_user)
):
    """Get chat history for a session"""
    try:
        conversation = await conversation_manager.get_session(request.session_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if user has access to this session
        if conversation.user_id != user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        messages = conversation.get_messages(
            limit=request.limit,
            before_timestamp=request.before_timestamp
        )
        
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

@router.delete("/chat/session/{session_id}")
async def delete_chat_session(
    session_id: str,
    user = Depends(get_current_user)
):
    """Delete a chat session and its history"""
    try:
        success = await conversation_manager.delete_session(
            session_id=session_id,
            user_id=user["id"]
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found or access denied")
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")

# =============================================================================
# Export Status Endpoints
# =============================================================================

@router.get("/export/status/{job_id}")
async def get_export_status(
    job_id: str,
    user = Depends(get_current_user)
):
    """Get the status of an export job"""
    try:
        status = await queue_service.get_export_status(job_id)
        return status
        
    except Exception as e:
        logger.error(f"Failed to get export status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get export status")
