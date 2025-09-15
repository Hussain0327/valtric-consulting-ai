"""
Pydantic Models and Schemas for ValtricAI Consulting Agent

Defines request/response models, database schemas, and data validation
for the dual RAG consulting AI system.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, validator


# =============================================================================
# Enums
# =============================================================================

class ConsultantPersona(str, Enum):
    """AI consultant personas with different expertise levels"""
    ASSOCIATE = "associate"       # Junior consultant - GPT-4
    PARTNER = "partner"           # Senior consultant - GPT-4
    SENIOR_PARTNER = "senior_partner"  # Executive consultant - GPT-4

class ConsultingFramework(str, Enum):
    """Available consulting frameworks"""
    SWOT = "swot"
    PORTERS = "porters"
    MCKINSEY = "mckinsey"
    BCG_MATRIX = "bcg_matrix"
    ANSOFF = "ansoff"
    PESTEL = "pestel"

class MessageRole(str, Enum):
    """Chat message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class SessionStatus(str, Enum):
    """Chat session status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

# =============================================================================
# Chat Models
# =============================================================================

class ChatMessage(BaseModel):
    """Individual chat message"""
    id: str
    session_id: str
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class RetrievalSource(BaseModel):
    """RAG retrieval source information"""
    id: str
    text: str
    similarity_score: float = Field(ge=0.0, le=1.0)
    source_type: str  # "global" or "tenant"
    source_label: str  # "[Frameworks]" or "[Client]"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatResponse(BaseModel):
    """Complete chat response with structured data support"""
    session_id: str
    message: str
    persona: ConsultantPersona
    framework: Optional[ConsultingFramework] = None
    sources: List[RetrievalSource] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # New fields for structured data
    data_type: Optional[str] = "text"
    structured_data: Optional[Dict[str, Any]] = None
    chart_config: Optional[Dict[str, Any]] = None
    export_urls: Optional[Dict[str, str]] = None  # {"excel": url, "pdf": url, "ppt": url}
    has_attachments: bool = False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class StreamingChatResponse(BaseModel):
    """Streaming chat response chunk"""
    type: str  # "content", "sources", "complete", "error"
    content: Optional[str] = None
    sources: Optional[List[RetrievalSource]] = None
    session_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# =============================================================================
# Session Models
# =============================================================================

class ChatSessionCreate(BaseModel):
    """Create new chat session"""
    title: Optional[str] = Field(None, max_length=200)
    persona: ConsultantPersona = ConsultantPersona.PARTNER
    framework: Optional[ConsultingFramework] = None
    context: Dict[str, Any] = Field(default_factory=dict)

class ChatSessionUpdate(BaseModel):
    """Update existing chat session"""
    title: Optional[str] = Field(None, max_length=200)
    status: Optional[SessionStatus] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatSession(BaseModel):
    """Chat session information"""
    id: str
    user_id: str
    project_id: str
    title: str
    persona: ConsultantPersona
    framework: Optional[ConsultingFramework] = None
    status: SessionStatus
    message_count: int = 0
    last_activity: datetime
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# =============================================================================
# Framework Models
# =============================================================================

class SWOTAnalysisInput(BaseModel):
    """Input for SWOT analysis"""
    company_description: str = Field(..., min_length=10, max_length=2000)
    industry: Optional[str] = None
    timeframe: Optional[str] = None
    specific_focus: Optional[str] = None

class SWOTAnalysisResult(BaseModel):
    """SWOT analysis results"""
    strengths: List[str]
    weaknesses: List[str] 
    opportunities: List[str]
    threats: List[str]
    strategic_recommendations: List[str]
    confidence_score: float = Field(ge=0.0, le=1.0)
    sources_used: List[RetrievalSource] = Field(default_factory=list)

class PortersFiveForcesInput(BaseModel):
    """Input for Porter's Five Forces analysis"""
    company_description: str = Field(..., min_length=10, max_length=2000)
    industry: str = Field(..., min_length=2, max_length=100)
    market_segment: Optional[str] = None

class PortersFiveForcesResult(BaseModel):
    """Porter's Five Forces analysis results"""
    competitive_rivalry: Dict[str, Any]
    supplier_power: Dict[str, Any]
    buyer_power: Dict[str, Any]
    threat_of_substitution: Dict[str, Any]
    barriers_to_entry: Dict[str, Any]
    overall_attractiveness: str
    strategic_implications: List[str]
    confidence_score: float = Field(ge=0.0, le=1.0)

# =============================================================================
# Document Models
# =============================================================================

class DocumentUpload(BaseModel):
    """Document upload request"""
    filename: str = Field(..., max_length=255)
    content_type: str
    content: str  # Base64 encoded or plain text
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator("content_type")
    def validate_content_type(cls, v):
        allowed_types = [
            "text/plain", "text/markdown", "text/csv",
            "application/pdf", "application/json",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        if v not in allowed_types:
            raise ValueError(f"Content type {v} not supported")
        return v

class DocumentInfo(BaseModel):
    """Document information"""
    id: str
    filename: str
    content_type: str
    size: int
    chunk_count: int
    upload_date: datetime
    processed: bool
    metadata: Dict[str, Any] = Field(default_factory=dict)

# =============================================================================
# Feedback Models
# =============================================================================

class FeedbackType(str, Enum):
    """Types of feedback"""
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request" 
    GENERAL_FEEDBACK = "general_feedback"
    AI_RESPONSE_QUALITY = "ai_response_quality"
    USABILITY = "usability"
    PERFORMANCE = "performance"

class FeedbackSeverity(str, Enum):
    """Feedback severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FeedbackSubmission(BaseModel):
    """User feedback submission"""
    type: FeedbackType
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    severity: FeedbackSeverity = FeedbackSeverity.MEDIUM
    session_id: Optional[str] = None
    message_id: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    context: Dict[str, Any] = Field(default_factory=dict)

class FeedbackResponse(BaseModel):
    """Feedback submission response"""
    feedback_id: str
    status: str = "received"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    estimated_response_time: Optional[str] = None

class ResponseRating(BaseModel):
    """AI response quality rating"""
    session_id: str
    message_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)
    aspects: Dict[str, int] = Field(default_factory=dict)  # e.g., {"accuracy": 4, "helpfulness": 5}

# =============================================================================
# Analytics Models
# =============================================================================

class UsageMetrics(BaseModel):
    """Usage analytics"""
    user_id: str
    project_id: str
    messages_sent: int
    tokens_used: int
    sessions_created: int
    frameworks_used: Dict[str, int] = Field(default_factory=dict)
    period_start: datetime
    period_end: datetime

class SystemHealth(BaseModel):
    """System health status"""
    global_rag_healthy: bool
    tenant_rag_healthy: bool
    openai_healthy: bool
    database_healthy: bool
    last_check: datetime
    response_times: Dict[str, float] = Field(default_factory=dict)

# =============================================================================
# Error Models
# =============================================================================

class APIError(BaseModel):
    """Standard API error response"""
    error: str
    detail: str
    code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationError(BaseModel):
    """Validation error details"""
    field: str
    message: str
    invalid_value: Any

# =============================================================================
# User & Auth Models
# =============================================================================

class UserProfile(BaseModel):
    """User profile information"""
    id: str
    email: str
    full_name: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    subscription_tier: str = "free"
    usage_limits: Dict[str, int] = Field(default_factory=dict)
    created_at: datetime
    last_active: datetime

class ProjectInfo(BaseModel):
    """Project information"""
    id: str
    name: str
    organization_id: str
    tier: str = "pro"
    created_at: datetime
    document_count: int = 0
    session_count: int = 0