"""
Feedback and Analytics Routes for ValtricAI Consulting Agent
Comprehensive feedback collection and usage analytics system
"""

import logging
from datetime import datetime, timedelta
from uuid import uuid4
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks

from api.dependencies import get_current_user, get_project_id
from models.schemas import (
    FeedbackSubmission,
    FeedbackResponse,
    ResponseRating,
    UsageMetrics
)
from rag_system.supabase_client import supabase_manager
from utils.tracing import RequestTracer, set_current_trace

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackSubmission,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user),
    project_id = Depends(get_project_id)
):
    """
    Submit comprehensive user feedback
    
    Supports various feedback types:
    - Bug reports
    - Feature requests
    - AI response quality feedback
    - General usability feedback
    - Performance issues
    """
    
    # Initialize tracing
    tracer = RequestTracer(route="POST /feedback", user_id=user.get("id"))
    set_current_trace(tracer)
    
    try:
        tracer.set_intent("submit_feedback")
        feedback_id = str(uuid4())
        
        # Prepare feedback data for storage
        feedback_data = {
            "id": feedback_id,
            "user_id": user.get("id"),
            "project_id": project_id,
            "type": feedback.type.value,
            "title": feedback.title,
            "description": feedback.description,
            "severity": feedback.severity.value,
            "session_id": feedback.session_id,
            "message_id": feedback.message_id,
            "rating": feedback.rating,
            "context": feedback.context,
            "status": "open",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Store feedback in Supabase tenant database
        result = supabase_manager.tenant_admin_client.table("user_feedback").insert(feedback_data).execute()
        
        if not result.data:
            logger.error(f"Failed to store feedback {feedback_id}")
            raise HTTPException(status_code=500, detail="Failed to store feedback")
        
        # Determine estimated response time based on severity
        response_times = {
            "critical": "Within 2 hours",
            "high": "Within 24 hours", 
            "medium": "Within 3 business days",
            "low": "Within 1 week"
        }
        
        estimated_response = response_times.get(feedback.severity.value, "Within 1 week")
        
        logger.info(f"Feedback submitted: {feedback_id} - Type: {feedback.type.value}, Severity: {feedback.severity.value}")
        
        # Background task to process feedback (notifications, categorization, etc.)
        background_tasks.add_task(_process_feedback_background, feedback_data)
        
        return FeedbackResponse(
            feedback_id=feedback_id,
            status="received",
            timestamp=datetime.utcnow(),
            estimated_response_time=estimated_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        tracer.set_error(str(e))
        logger.error(f"Feedback submission failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")
    finally:
        background_tasks.add_task(tracer.finish)


@router.post("/feedback/rating")
async def rate_ai_response(
    rating: ResponseRating,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user),
    project_id = Depends(get_project_id)
):
    """
    Rate AI response quality
    
    Allows users to provide detailed ratings on:
    - Overall response quality (1-5 stars)
    - Specific aspects (accuracy, helpfulness, etc.)
    - Additional comments
    """
    
    tracer = RequestTracer(route="POST /feedback/rating", user_id=user.get("id"))
    set_current_trace(tracer)
    
    try:
        tracer.set_intent("rate_response")
        rating_id = str(uuid4())
        
        # Prepare rating data
        rating_data = {
            "id": rating_id,
            "user_id": user.get("id"),
            "project_id": project_id,
            "session_id": rating.session_id,
            "message_id": rating.message_id,
            "overall_rating": rating.rating,
            "comment": rating.comment,
            "aspects": rating.aspects,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store in database
        result = supabase_manager.tenant_admin_client.table("response_ratings").insert(rating_data).execute()
        
        if not result.data:
            logger.error(f"Failed to store rating {rating_id}")
            raise HTTPException(status_code=500, detail="Failed to store rating")
        
        logger.info(f"Response rated: {rating.session_id}/{rating.message_id} - Rating: {rating.rating}/5")
        
        return {
            "rating_id": rating_id,
            "status": "recorded",
            "message": "Thank you for your feedback!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        tracer.set_error(str(e))
        logger.error(f"Rating submission failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit rating")
    finally:
        background_tasks.add_task(tracer.finish)


@router.get("/analytics/usage", response_model=UsageMetrics)
async def get_usage_analytics(
    days: int = 30,
    user = Depends(get_current_user),
    project_id = Depends(get_project_id)
):
    """
    Get comprehensive usage analytics for the user/project
    
    Returns:
    - Message counts
    - Token usage
    - Session statistics
    - Framework usage breakdown
    - Time period analysis
    """
    
    try:
        user_id = user.get("id")
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get session count
        session_result = supabase_manager.tenant_client.table("chat_sessions").select(
            "id, created_at"
        ).eq("user_id", user_id).eq("project_id", project_id).gte(
            "created_at", start_date.isoformat()
        ).execute()
        
        session_count = len(session_result.data or [])
        
        # Get message count from sessions
        message_count = 0
        if session_result.data:
            session_ids = [s["id"] for s in session_result.data]
            
            # Count messages across all sessions
            for session_id in session_ids:
                msg_result = supabase_manager.tenant_client.table("chat_messages").select(
                    "id", count="exact"
                ).eq("session_id", session_id).execute()
                
                if msg_result.count:
                    message_count += msg_result.count
        
        # Get token usage from tracing logs (this would require a traces table)
        # For now, estimate based on message count
        estimated_tokens = message_count * 150  # Rough estimate
        
        # Framework usage (would need to track this in session metadata or separate table)
        frameworks_used = {
            "swot": 0,
            "porters": 0, 
            "mckinsey": 0,
            "general": session_count
        }
        
        return UsageMetrics(
            user_id=user_id,
            project_id=project_id,
            messages_sent=message_count,
            tokens_used=estimated_tokens,
            sessions_created=session_count,
            frameworks_used=frameworks_used,
            period_start=start_date,
            period_end=end_date
        )
        
    except Exception as e:
        logger.error(f"Usage analytics failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve usage analytics")


@router.get("/analytics/feedback/summary")
async def get_feedback_summary(
    days: int = 30,
    user = Depends(get_current_user),
    project_id = Depends(get_project_id)
):
    """Get feedback summary for the project"""
    
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get feedback count by type and severity
        feedback_result = supabase_manager.tenant_client.table("user_feedback").select(
            "type, severity, status, created_at"
        ).eq("project_id", project_id).gte(
            "created_at", start_date.isoformat()
        ).execute()
        
        feedback_data = feedback_result.data or []
        
        # Analyze feedback
        type_counts = {}
        severity_counts = {}
        status_counts = {}
        
        for feedback in feedback_data:
            # Count by type
            feedback_type = feedback["type"]
            type_counts[feedback_type] = type_counts.get(feedback_type, 0) + 1
            
            # Count by severity
            severity = feedback["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Count by status
            status = feedback["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Get average ratings
        rating_result = supabase_manager.tenant_client.table("response_ratings").select(
            "overall_rating"
        ).eq("project_id", project_id).gte(
            "created_at", start_date.isoformat()
        ).execute()
        
        ratings = [r["overall_rating"] for r in (rating_result.data or [])]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        return {
            "period_days": days,
            "total_feedback": len(feedback_data),
            "feedback_by_type": type_counts,
            "feedback_by_severity": severity_counts,
            "feedback_by_status": status_counts,
            "total_ratings": len(ratings),
            "average_rating": round(avg_rating, 2),
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Feedback summary failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve feedback summary")


async def _process_feedback_background(feedback_data: dict):
    """Background task to process feedback submissions"""
    
    try:
        # Log for monitoring
        logger.info(f"Processing feedback {feedback_data['id']}: {feedback_data['type']}")
        
        # For critical/high severity issues, could send notifications
        if feedback_data["severity"] in ["critical", "high"]:
            logger.warning(f"High priority feedback received: {feedback_data['id']}")
            # Could integrate with Slack, email, etc.
        
        # Could run auto-categorization, sentiment analysis, etc.
        # For now, just log the processing
        
    except Exception as e:
        logger.error(f"Background feedback processing failed: {e}")