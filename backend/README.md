# Backend - AI Agents & API

```
backend/
├── __init__.py
├── main.py                           # FastAPI application entry point
├── config/
│   ├── __init__.py
│   ├── settings.py                   # Environment configuration
│   ├── database.py                   # Database connections
│   └── logging.py                    # Logging configuration
│
├── rag_system/
│   ├── __init__.py
│   ├── supabase_client.py           # Vector database client
│   ├── document_processor.py        # Document chunking and embedding
│   ├── retriever.py                 # RAG retrieval logic
│   ├── embeddings.py                # Embedding generation
│   └── knowledge_base/
│       ├── __init__.py
│       ├── consulting_frameworks.py  # SWOT, Porter's 5, etc.
│       ├── industry_data.py         # Market research
│       └── client_context.py        # Client-specific data
│
├── agent_logic/
│   ├── __init__.py
│   ├── base_agent.py                # Abstract consultant agent
│   ├── personas/
│   │   ├── __init__.py
│   │   ├── associate.py             # Junior consultant (GPT-5-nano)
│   │   ├── partner.py               # Senior consultant (GPT-5-mini)
│   │   └── senior_partner.py        # Executive consultant (GPT-5)
│   ├── complexity_analyzer.py       # Query complexity assessment
│   ├── model_router.py              # GPT model selection
│   ├── conversation_manager.py      # Session and context management
│   ├── framework_selector.py        # Consulting framework selection
│   └── response_synthesizer.py      # RAG + LLM response combination
│
├── models/
│   ├── __init__.py
│   ├── openai_client.py             # GPT-5 API client
│   ├── schemas.py                   # Pydantic models
│   └── database_models.py           # Database table definitions
│
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py                  # Chat endpoints
│   │   ├── sessions.py              # Session management
│   │   ├── frameworks.py            # Framework endpoints
│   │   ├── analysis.py              # Analysis tools
│   │   ├── feedback.py              # User feedback
│   │   └── health.py                # Health checks
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py                  # Authentication
│   │   ├── rate_limiting.py         # Rate limiting
│   │   ├── cors.py                  # CORS handling
│   │   └── error_handling.py        # Error middleware
│   ├── dependencies.py              # FastAPI dependencies
│   └── exceptions.py                # Custom exceptions
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py              # Authentication logic
│   ├── session_service.py           # Session management
│   ├── analytics_service.py         # Usage analytics
│   ├── notification_service.py      # Notifications
│   └── cache_service.py             # Redis caching
│
├── utils/
│   ├── __init__.py
│   ├── text_processing.py           # Text utilities
│   ├── validators.py                # Input validation
│   ├── formatters.py                # Response formatting
│   ├── security.py                  # Security utilities
│   └── monitoring.py                # Performance monitoring
│
└── ml/
    ├── __init__.py
    ├── feedback_processor.py        # User feedback analysis
    ├── model_optimizer.py           # Model performance optimization
    ├── usage_analyzer.py            # Usage pattern analysis
    └── recommendation_engine.py     # Personalization engine
```

## Key Backend Components:

**rag_system/**: Vector database and knowledge retrieval
**agent_logic/**: Consultant personas and reasoning
**api/**: REST API endpoints and middleware
**services/**: Business logic services
**ml/**: Machine learning and optimization