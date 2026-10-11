# AI Software Engineering Agent

> An AI-powered multi-agent system that understands software repositories, analyzes code, identifies issues, proposes safe code changes, and generates test cases using RAG and LLM-based agent orchestration.

## Overview

**AI Software Engineering Agent** is a production-style backend application designed to help developers interact with an uploaded source-code repository using natural language.

Instead of relying on a single LLM prompt, the system uses a **LangGraph-based multi-agent workflow**. A Planner Agent first understands the user's request and routes it to the appropriate specialized agent.

The system currently supports:

- **Code Analysis** — Understand and explain repository code and behavior.
- **Code Review** — Identify bugs, validation issues, and code-quality concerns.
- **Code Modification** — Generate proposed source-code changes.
- **Test Generation** — Create normal, boundary, invalid-input, and failure test scenarios.

For code modifications, the system uses a **Human-in-the-Loop approval workflow**. AI-generated changes are stored as proposals and are never applied directly to the repository without explicit approval.

## Why This Project?

Most AI coding applications focus only on generating code. This project focuses on the broader software engineering workflow:

```text
Repository → RAG Retrieval → Agent Routing → Specialized Agent
                                      ↓
                         Analysis / Review / Testing
                                      ↓
                           Code Modification Proposal
                                      ↓
                            Human Approval Required
                                      ↓
                         Safe Apply → Backup → Rollback
```

The goal is to demonstrate practical AI engineering concepts including:

- Multi-agent orchestration
- Retrieval-Augmented Generation
- Semantic code search
- LLM integration
- Human-in-the-loop workflows
- Persistent vector storage
- Transaction-safe code modification
- Backup and rollback strategies
- AI observability with LangSmith

# Key Features

### Multi-Agent Task Routing

A Planner Agent classifies each request and dynamically routes it through the LangGraph workflow.

| Task                | Agent                   | Purpose                          |
| ------------------- | ----------------------- | -------------------------------- |
| `ANALYSIS`          | Code Analysis Agent     | Understand code behavior         |
| `CODE_REVIEW`       | Code Review Agent       | Identify bugs and quality issues |
| `CODE_MODIFICATION` | Code Modification Agent | Propose source-code changes      |
| `TESTING`           | Testing Agent           | Generate structured test cases   |

### Repository-Aware RAG

The system answers questions using the actual uploaded repository.

```text
ZIP Repository
      ↓
Extract Source Code
      ↓
Chunk Code
      ↓
Generate Embeddings
      ↓
Repository-Specific FAISS Index
      ↓
Semantic Retrieval
      ↓
Context-Aware LLM Response
```

Each repository maintains its own vector index, allowing repository-specific retrieval and persistent storage.

### Human-in-the-Loop Code Changes

AI-generated code is **never directly applied**.

```text
User Request
     ↓
Code Modification Agent
     ↓
Generate Proposed Changes
     ↓
Store Change Request
     ↓
PENDING APPROVAL
     ↓
Approve / Reject
     ↓
Verify Original Code
     ↓
Create Backup
     ↓
Apply Changes
     ↓
APPLIED / FAILED
```

### Safe Code Application

Before modifying source code, the application:

- Verifies that the target file exists.
- Validates the original code before replacement.
- Handles whitespace and line-ending differences.
- Creates a backup before modification.
- Tracks change-request status.
- Restores successfully modified files if a later operation fails.

---

# Observability

The application integrates **LangSmith** for tracing the AI workflow.

Traces include:

- LangGraph workflow execution
- Planner Agent routing
- Specialized agent execution
- Code retrieval
- Embedding generation
- FAISS search
- LLM calls
- Inputs, outputs, latency, and failures

This provides end-to-end visibility into how each AI request moves through the system.

---

# Tech Stack

**Backend**

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

**AI & Agents**

- LangChain
- LangGraph
- LangSmith
- Groq LLM

**RAG**

- Embeddings
- FAISS
- Semantic Retrieval
- Code Chunking
- Context-Aware Prompting

**Data & Infrastructure**

- PostgreSQL
- Docker
- Docker Compose

---

# API Example

### Analyze Code

```text
POST /api/v1/agent
```

**Request**

```json
{
  "repository_id": 8,
  "question": "Analyze what AddProduct.java does."
}
```

### Propose a Code Modification

```json
{
  "repository_id": 8,
  "question": "Fix AddProduct.java so that product price cannot be negative."
}
```

**Response**

```json
{
  "task_type": "CODE_MODIFICATION",
  "answer": {
    "status": "PENDING_APPROVAL",
    "change_request_id": 2,
    "message": "Code changes were proposed and saved. Human approval is required before the changes can be applied."
  }
}
```

---

# Getting Started

## Clone the Repository

```bash
git clone <your-repository-url>
cd AI-Software-Engineering-Agent
```

## Create a Virtual Environment

````

## Install Dependencies

```bash
pip install -r requirements.txt
````

## Configure Environment Variables

Create a `.env` file:

```env
APP_NAME=AI Software Engineering Agent
API_V1_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000

DATABASE_URL=your_postgresql_connection_url

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_groq_model

STORAGE_ROOT=storage

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=AI-Software-Engineering-Agent
```

> Never commit `.env` files or API keys to GitHub.

## Run Database Migrations

```bash
alembic upgrade head
```

## Start the Application

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

---

# Docker

Start the application and required services:

```bash
docker compose up --build
```

---

# Future Enhancements

- Automated test execution after code changes
- Git integration and pull request creation
- Redis-based semantic and prompt caching
- Background processing with Kafka
- Role-based authentication
- CI/CD pipeline
- AWS deployment
- Repository-level agent memory
- Support for additional programming languages

---

# Key Engineering Concepts Demonstrated

This project demonstrates hands-on experience with:

**Multi-Agent Systems · LangGraph · LangChain · RAG · FAISS · Semantic Search · LLM Integration · AI Code Analysis · AI Code Review · AI-Assisted Code Modification · Human-in-the-Loop Workflows · Transaction Handling · Backup & Rollback · FastAPI · PostgreSQL · SQLAlchemy · Alembic · Docker · LangSmith Observability**

---

## Project Status

**Core multi-agent workflow, repository RAG, human approval, safe code application, persistent vector storage, code review, test generation, and LangSmith tracing are implemented and working.**
