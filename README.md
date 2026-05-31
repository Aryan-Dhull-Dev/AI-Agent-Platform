# AI Agent Platform

> Cloud-native AI agent orchestration platform with tool-calling agents, conversational memory, and production-grade GCP deployment.

## 🌟 Features

- ✅ **Tool-calling AI Agents** — Llama 3.1 70B via Groq API with MCP (Model Context Protocol) tools
- ✅ **Conversational Memory** — Session persistence with message history retrieval
- ✅ **Authentication** — JWT-based auth with secure password hashing (bcrypt)
- ✅ **Production Deployment** — GCP Cloud Run + Cloud SQL with health checks
- ✅ **Token Analytics** — Track input/output tokens, cost per request
- ✅ **async/await Architecture** — Full async support for high concurrency
- ✅ **Structured Logging** — JSON logs for production monitoring
- ✅ **Database Migrations** — Alembic for schema versioning

***

## 🏗️ Architecture

```
Client (Browser/API)
       ↓
FastAPI API Gateway (Port 8000)
       ↓
Agent Orchestrator (LangGraph)
       ↓
MCP Tool Layer
   ├── Postgres Tool (query_postgres)
   ├── File Tool (read_file, write_file)
   ├── Web Search Tool (duckduckgo_search)
   └── Docker/GCP Tool (deploy_service)
       ↓
Groq API (Llama 3.1 70B)
       ↓
PostgreSQL (Cloud SQL)
```

***

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (or Docker Engine)
- Python 3.11+ (optional, for local development)
- Groq API key (free at https://console.groq.com)

### 1. Clone Repository

```bash
git clone https://github.com/Aryan-Dhull-Dev/AI-Agent-Platform
cd ai-agent-platform
```

### 2. Environment Setup

```bash
# Create .env file
cp .env.example .env

# Edit .env with your credentials
# Required:
# - GROQ_API_KEY
# - SECRET_KEY (generate with: openssl rand -hex 32)
```

### 3. Run with Docker

```bash
# Start all services (FastAPI + PostgreSQL)
docker compose up --build

# API will be available at:
# http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

### 4. Local Development (Optional)

```bash
# Terminal 1: Start PostgreSQL in Docker
docker compose up db

# Terminal 2: Run FastAPI locally
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

***

## 📚 API Documentation

### Authentication

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/signup` | POST | ❌ No | Create new user |
| `/api/auth/login` | POST | ❌ No | Login and get JWT token |
| `/api/auth/me` | GET | ✅ Yes | Get current user info |
| `/api/auth/sessions` | GET | ✅ Yes | Get all chat sessions |

### Chat & Agents

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/chat` | POST | ✅ Yes | Send message to AI agent |
| `/api/chat?session_id=X` | POST | ✅ Yes | Chat in existing session |
| `/api/history?session_id=X` | GET | ✅ Yes | Get chat history |
| `/api/agents` | GET | ✅ Yes | List available agents |

### System

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | ❌ No | Health check (Cloud Run) |
| `/` | GET | ❌ No | Root endpoint |
| `/test-db` | GET | ❌ No | Test database connection |
| `/docs` | GET | ❌ No | Swagger UI documentation |
| `/openapi.json` | GET | ❌ No | OpenAPI schema |

***

## 🔐 Authentication Flow

```
1. User Signup
   POST /api/auth/signup
   { "email": "user@example.com", "password": "password123" }
   → Returns: User object with id

2. User Login
   POST /api/auth/login
   { "email": "user@example.com", "password": "password123" }
   → Returns: { "access_token": "eyJ...", "token_type": "bearer", "user": {...} }

3. Use Token in Protected Routes
   POST /api/chat
   Headers: { "Authorization": "Bearer eyJ..." }
   Body: { "message": "Hello, AI!" }
   → Returns: AI response with token usage
```

***

## 🗂️ Project Structure

```
ai-agent-platform/
├── app/
│   ├── api/                  # API routes
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication endpoints
│   │   └── chat.py           # Chat & agent endpoints
│   ├── agents/               # AI agent orchestration
│   │   ├── __init__.py
│   │   └── orchestrator.py   # LangGraph agent workflow
│   ├── core/                 # Core utilities
│   │   ├── __init__.py
│   │   ├── settings.py         # Settings & environment
│   │   ├── security.py       # JWT & password hashing
│   │   └── auth.py           # Authentication dependencies
│   ├── db/                   # Database layer
│   │   ├── __init__.py
│   │   ├── models.py         # SQLAlchemy models
│   │   └── session.py        # DB session & engine
│   ├── mcp/                  # MCP tools
│   │   ├── __init__.py
│   │   └── server.py         # MCP tool registration
│   ├── schemas/              # Pydantic schemas
│   │   └── __init__.py
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   └── ai_service.py     # Groq API integration
│   ├── main.py               # FastAPI app entry point
├── docker-compose.yml        # Docker orchestration
├── Dockerfile                # Production container
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (gitignored)
├── .env.example              # Example environment file
└── README.md                 # This file
```

***

## 🛠️ Tech Stack

### Core
- **FastAPI** — Modern async web framework
- **PostgreSQL** — Relational database (async with `asyncpg`)
- **SQLAlchemy 2.0** — ORM with async support
- **Pydantic v2** — Data validation
- **Alembic** — Database migrations

### AI & Orchestration
- **Groq API** — Llama 3.1 70B (free, fast inference)
- **LangGraph** — Agent orchestration & state management
- **MCP (Model Context Protocol)** — Tool calling framework

### Cloud & DevOps
- **Docker** — Containerization
- **GCP Cloud Run** — Serverless deployment
- **GCP Cloud SQL** — Managed PostgreSQL
- **GCP Artifact Registry** — Container image storage

***

## 📊 Database Schema

```sql
-- Users table
users (
  id          SERIAL PRIMARY KEY,
  email       VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- Chat sessions table
chat_sessions (
  id          SERIAL PRIMARY KEY,
  user_id     INTEGER REFERENCES users(id),
  title       VARCHAR(255) DEFAULT 'New Chat',
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- Messages table
messages (
  id          SERIAL PRIMARY KEY,
  session_id  INTEGER REFERENCES chat_sessions(id),
  role        VARCHAR(50) NOT NULL,  -- 'user' or 'assistant'
  content     TEXT NOT NULL,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- Agent executions table
agent_executions (
  id          SERIAL PRIMARY KEY,
  user_id     INTEGER REFERENCES users(id),
  session_id  INTEGER REFERENCES chat_sessions(id),
  prompt      TEXT NOT NULL,
  response    TEXT NOT NULL,
  tokens_input  INTEGER DEFAULT 0,
  tokens_output INTEGER DEFAULT 0,
  tokens_total  INTEGER DEFAULT 0,
  cost_usd    FLOAT DEFAULT 0.0,
  model_used  VARCHAR(100) DEFAULT 'llama-3.1-70b-versatile',
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

***

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/agent_db

# Server
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32

# AI
GROQ_API_KEY=gsk_your_key_here
AI_MODEL=llama-3.1-70b-versatile
```

### Generate SECRET_KEY

```bash
openssl rand -hex 32
# Output: 8f3a9b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a
```

***

## 🧪 Testing

```bash
# Run tests (if configured)
pytest

# Test specific endpoint
curl http://localhost:8000/health

# Test authentication flow
# 1. Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 2. Login (copy access_token)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 3. Use token in protected route
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, AI!"}'
```

***

## 📦 Deployment to GCP

### 1. Setup GCP Project

```bash
export PROJECT_ID="your-unique-project-id"
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# Enable services
gcloud services enable cloudbuild.googleapis.com containerregistry.googleapis.com run.googleapis.com sqladmin.googleapis.com
```

### 2. Build & Push Docker Image

```bash
# Create Artifact Registry
gcloud artifacts repositories create fastapi-repo \
  --repository-format=docker \
  --location=us-central1

# Build and push
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/fastapi-repo/fastapi-agent
```

### 3. Create Cloud SQL Instance

```bash
gcloud sql instances create agent-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

gcloud sql databases create agent_db --instance=agent-db
```

### 4. Deploy to Cloud Run

```bash
gcloud run deploy fastapi-agent \
  --image us-central1-docker.pkg.dev/$PROJECT_ID/fastapi-repo/fastapi-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars DATABASE_URL="postgresql+asyncpg://user:password@/agent_db?host=/cloudsql/PROJECT:REGION:INSTANCE" \
  --set-secrets GROQ_API_KEY="GROQ_KEY:latest" \
  --set-secrets SECRET_KEY="SECRET_KEY:latest"
```

***

## 📈 Monitoring & Observability

### Token Usage Analytics

```sql
-- Total tokens used
SELECT SUM(tokens_total) as total_tokens FROM agent_executions;

-- Average cost per request
SELECT AVG(cost_usd) as avg_cost FROM agent_executions;

-- Most active user
SELECT u.email, COUNT(ae.id) as requests
FROM users u
JOIN agent_executions ae ON u.id = ae.user_id
GROUP BY u.id
ORDER BY requests DESC
LIMIT 10;
```

### Logs Format

```json
{"level":"INFO","time":"2026-05-30T12:00:00Z","message":"Request completed","path":"/api/chat","latency_sec":0.234}
```

***

## 🚧 Roadmap

### Stretch Goals
- Redis queues + Celery workers
- RAG with vector search (pgvector)
- Multi-agent collaboration
- Terraform IaC
- Kubernetes deployment

***

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

***

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

***

## 👨‍💻 Author

Built as a cloud-native AI engineering showcase project.

**Tech Stack Highlight:** FastAPI + Groq (Llama 3.1 70B) + LangGraph + MCP + PostgreSQL + Docker + GCP Cloud Run

***

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — Modern web framework
- [Groq](https://groq.com/) — Fast, free LLM inference
- [LangChain/LangGraph](https://langchain-ai.github.io/langgraph/) — Agent orchestration
- [MCP](https://modelcontextprotocol.io/) — Tool calling protocol
- [PostgreSQL](https://www.postgresql.org/) — Powerful open-source database

***

**Deployed on GCP Cloud Run:** https://your-app.us-central1.run.app

**Live API Docs:** https://your-app.us-central1.run.app/docs

***

<div align="center">

**⭐ If this project helped you, consider giving it a star!**

Made with ❤️ using FastAPI + Groq + LangGraph + PostgreSQL + Docker + GCP

</div>
