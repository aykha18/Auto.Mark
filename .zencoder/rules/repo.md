---
description: Repository Information Overview
alwaysApply: true
---

# Repository Information Overview

## Repository Summary
AI Marketing Agents is a comprehensive, enterprise-grade AI marketing platform featuring intelligent LLM routing, advanced RAG systems, multi-agent orchestration, and complete production infrastructure for autonomous marketing campaign execution with real-time optimization and behavioral intelligence.

## Repository Structure
The repository contains a full-stack application with separate backend and frontend components, documentation, database migrations, and deployment configurations.

### Main Repository Components
- **Backend API**: FastAPI-based microservice handling AI agents, RAG, and data processing
- **Frontend**: React TypeScript application for user interface and landing pages
- **Documentation**: Comprehensive guides and architecture documentation
- **Database**: Alembic migrations for PostgreSQL schema management
- **Vector Database**: ChromaDB for embeddings and RAG retrieval
- **Deployment**: Docker, Railway, and cloud infrastructure configurations

## Projects

### Backend (Python/FastAPI)
**Configuration File**: requirements.txt

#### Language & Runtime
**Language**: Python
**Version**: 3.10+
**Runtime**: FastAPI with uvicorn ASGI server
**Build System**: pip
**Package Manager**: pip

#### Dependencies
**Main Dependencies**:
- fastapi, uvicorn (web framework)
- sqlalchemy, asyncpg, alembic (database)
- openai, langchain-core, langchain-openai, langchain-community (AI/ML)
- chromadb, sentence-transformers (vector database)
- httpx, aiohttp (HTTP clients)
- stripe, razorpay (payments)
- sendgrid (email)

**Development Dependencies**:
- python-dotenv, pydantic, pydantic-settings (configuration)
- structlog, prometheus-client (monitoring)

#### Build & Installation
```bash
pip install -r requirements.txt
alembic upgrade head
```

#### Main Files & Resources
**Entry Point**: app/main.py
**API Routes**: app/api/
**Agents**: app/agents/
**Database Models**: app/models/
**RAG System**: app/rag/
**LLM Router**: app/llm/

#### Docker
**Dockerfile**: Dockerfile (multi-stage build combining frontend and backend)
**Configuration**: Builds frontend, installs Python deps, serves via uvicorn on port 3000

### Frontend (React/TypeScript)
**Configuration File**: frontend/package.json

#### Language & Runtime
**Language**: TypeScript
**Version**: 4.9.5
**Runtime**: React 18.3.1 with Node.js 18+
**Build System**: npm
**Package Manager**: npm

#### Dependencies
**Main Dependencies**:
- react, react-dom, react-router-dom (framework)
- axios (HTTP client)
- lucide-react (icons)
- @stripe/react-stripe-js, @stripe/stripe-js (payments)

**Development Dependencies**:
- tailwindcss, autoprefixer, postcss (styling)
- lighthouse, serve (performance testing)
- @types/* (TypeScript types)
- @testing-library/* (testing)

#### Build & Installation
```bash
cd frontend
npm install
npm run build
```

#### Main Files & Resources
**Entry Point**: src/index.tsx
**Main Component**: src/App.tsx
**Components**: src/components/
**Pages**: src/pages/
**Services**: src/services/
**Types**: src/types/

#### Testing
**Framework**: Jest with React Testing Library
**Test Location**: src/
**Naming Convention**: *.test.tsx
**Configuration**: setupTests.ts
**Run Command**:
```bash
npm test
```

#### Docker
**Configuration**: Built as part of multi-stage Dockerfile, static files served by backend