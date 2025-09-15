# ValtricAI Consulting Agent

## Project Overview

A sophisticated AI-powered consulting platform that combines multiple GPT models with RAG (Retrieval-Augmented Generation) to provide expert business consulting across various frameworks and methodologies.

## Architecture

```
valtric-consulting-ai/
├── frontend/                           # React/Next.js UI Interface
│   └── README.md                       # Frontend structure & components
├── backend/                            # FastAPI + AI Agents
│   └── README.md                       # Backend structure & services
│
├── docs/
│   ├── api/
│   │   ├── openapi.json                 # OpenAPI specification
│   │   └── endpoints.md                 # API documentation
│   ├── architecture/
│   │   ├── system_design.md             # System architecture
│   │   ├── database_schema.md           # Database design
│   │   └── deployment.md                # Deployment guide
│   ├── frameworks/
│   │   ├── swot_analysis.md             # SWOT framework guide
│   │   ├── porters_five_forces.md       # Porter's framework guide
│   │   └── mckinsey_7s.md               # McKinsey 7S guide
│   ├── personas/
│   │   ├── consultant_personas.md       # Persona definitions
│   │   └── interaction_patterns.md      # Conversation patterns
│   └── deployment/
│       ├── local_setup.md               # Local development
│       ├── production_deploy.md         # Production deployment
│       └── monitoring.md                # Monitoring setup
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Pytest configuration
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_agents/
│   │   │   ├── __init__.py
│   │   │   ├── test_base_agent.py
│   │   │   ├── test_personas.py
│   │   │   └── test_complexity_analyzer.py
│   │   ├── test_rag/
│   │   │   ├── __init__.py
│   │   │   ├── test_retriever.py
│   │   │   ├── test_embeddings.py
│   │   │   └── test_document_processor.py
│   │   ├── test_api/
│   │   │   ├── __init__.py
│   │   │   ├── test_chat_routes.py
│   │   │   ├── test_auth.py
│   │   │   └── test_middleware.py
│   │   └── test_utils/
│   │       ├── __init__.py
│   │       ├── test_validators.py
│   │       └── test_formatters.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_full_conversation.py    # End-to-end conversation tests
│   │   ├── test_rag_integration.py      # RAG system integration
│   │   ├── test_model_routing.py        # Model selection integration
│   │   └── test_api_integration.py      # API integration tests
│   ├── performance/
│   │   ├── __init__.py
│   │   ├── test_load.py                 # Load testing
│   │   ├── test_concurrency.py          # Concurrent user testing
│   │   └── test_response_times.py       # Performance benchmarks
│   └── fixtures/
│       ├── __init__.py
│       ├── sample_queries.py            # Test query examples
│       ├── mock_responses.py            # Mock API responses
│       └── test_documents.py            # Test document samples
│
├── scripts/
│   ├── setup_database.py               # Database initialization
│   ├── populate_knowledge_base.py      # Load consulting frameworks
│   ├── run_migrations.py               # Database migrations
│   ├── performance_benchmark.py        # Performance testing
│   └── deploy.py                       # Deployment script
│
├── monitoring/
│   ├── health_checks.py                # System health monitoring
│   ├── metrics_collector.py            # Performance metrics
│   ├── alerts.py                       # Alert configuration
│   └── dashboards/
│       ├── grafana_config.json         # Grafana dashboard
│       └── prometheus.yml              # Prometheus configuration
│
└── infrastructure/
    ├── kubernetes/
    │   ├── deployment.yaml             # K8s deployment
    │   ├── service.yaml                # K8s service
    │   └── ingress.yaml                # K8s ingress
    ├── terraform/
    │   ├── main.tf                     # Infrastructure as code
    │   ├── variables.tf                # Terraform variables
    │   └── outputs.tf                  # Terraform outputs
    └── docker/
        ├── Dockerfile.prod             # Production Docker image
        └── docker-compose.prod.yml     # Production compose file
```

## Key Features

- **Multi-Persona AI Consultants**: Associate, Partner, and Senior Partner personas with different GPT models
- **RAG-Enhanced Responses**: Vector database integration for contextual consulting knowledge
- **Framework Integration**: SWOT, Porter's 5 Forces, McKinsey 7S, and more
- **Real-time Chat Interface**: WebSocket-powered consulting sessions
- **Session Management**: Persistent conversation history and analytics
- **Responsive UI**: Modern React/Next.js frontend with Tailwind CSS

## Quick Start

1. **Backend Setup**:
   ```bash
   cd backend/
   # See backend/README.md for setup instructions
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend/
   # See frontend/README.md for setup instructions
   ```

## Project Structure

- **`frontend/`**: User interface and client-side logic
- **`backend/`**: AI agents, API, and server-side services
- **`docs/`**: Complete project documentation
- **`tests/`**: Comprehensive testing suite
- **`infrastructure/`**: Deployment and monitoring configurations