"""
API Dependencies for ValtricAI Consulting Agent

Authentication and authorization dependencies for FastAPI routes.
"""

from typing import Dict, Any
from fastapi import HTTPException, Header, Depends
from rag_system.supabase_client import supabase_manager


async def get_current_user(authorization: str = Header(None)) -> Dict[str, Any]:
    """
    Extract and validate user from JWT token
    
    Args:
        authorization: Bearer token from Authorization header
    
    Returns:
        Dict containing user info
    
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Verify JWT token with Supabase
        response = supabase_manager.tenant_client.auth.get_user(token)
        
        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {
            "id": response.user.id,
            "email": response.user.email,
            "metadata": response.user.user_metadata or {}
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")


async def get_project_id(user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """
    Get project ID for the current user
    
    For now, we'll use a default project ID pattern.
    In production, this would come from user's organization/project association.
    
    Args:
        user: Current user info
    
    Returns:
        Project ID string
    """
    # For demo purposes, create a project ID based on user ID
    # In production, this would query the user's actual project memberships
    return f"proj_{user['id'][:8]}"


async def verify_admin_access(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Verify user has admin access
    
    Args:
        user: Current user info
    
    Returns:
        User dict if admin access verified
    
    Raises:
        HTTPException: If user lacks admin privileges
    """
    # Check if user has admin role in metadata
    user_metadata = user.get("metadata", {})
    role = user_metadata.get("role", "user")
    
    if role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user


async def get_optional_user(authorization: str = Header(None)) -> Dict[str, Any]:
    """
    Optionally get current user (for public endpoints that benefit from user context)
    
    Args:
        authorization: Optional Bearer token from Authorization header
    
    Returns:
        Dict containing user info, or None if no valid token
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None