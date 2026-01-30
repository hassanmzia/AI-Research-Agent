# AI Research Multi-Agent System

A professional-grade, full-stack application for **autonomous AGI research paper discovery and evaluation** powered by a hierarchical multi-agent architecture. The system uses LangChain/LangGraph agents, MCP (Model Context Protocol), and A2A (Agent-to-Agent) protocol to automate the entire research pipeline.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     React / TypeScript Frontend                  │
│         Dashboard │ Research │ Papers │ Collections              │
│                   (Port 3045)                                    │
├─────────────────────────────────────────────────────────────────┤
│                  Node.js API Gateway + WebSocket                 │
│          REST Proxy │ JWT Auth │ Real-time Updates               │
│                   (Port 3046)                                    │
├─────────────────────────────────────────────────────────────────┤
│                     Django REST API Backend                       │
│   Sessions │ Papers │ Evaluations │ MCP │ A2A │ Celery Tasks    │
│                   (Port 8045)                                    │
├──────────────┬──────────────┬───────────────┬───────────────────┤
│  PostgreSQL  │    Redis     │ Celery Worker │   Celery Beat     │
│   Database   │ Cache/Queue  │  (Async Jobs) │ (Scheduled Jobs)  │
│ (Port 5445)  │ (Port 6345)  │               │                   │
└──────────────┴──────────────┴───────────────┴───────────────────┘
```

## Key Features

### From the Original Notebook
- **Multi-Agent Research Pipeline**: Lead Supervisor -> Planner -> Discovery -> Evaluation -> Synthesis
- **ArXiv Paper Discovery**: Search with category filtering (cs.AI, cs.LG, cs.CL, cs.CV, cs.NE), date ranges, deduplication
- **10-Parameter AGI Evaluation Framework**: Weighted scoring across Novel Problem Solving, Few-Shot Learning, Task Transfer, Abstract Reasoning, Contextual Adaptation, Multi-Rule Integration, Generalization Efficiency, Meta-Learning, World Modeling, and Autonomous Goal Setting
- **LLM-Powered Planning**: AI generates execution plans with search keywords, strategies, and success criteria
- **Comprehensive Report Generation**: Markdown reports with executive summaries, top papers, score distribution, and recommendations
- **Retry Logic**: Exponential backoff with tenacity for API calls
- **Paper Validation and Deduplication**: Title normalization, abstract length checks

### Professional Enhancements
- **Full Authentication System**: JWT-based auth with registration, login, token refresh
- **Real-time WebSocket Updates**: Live pipeline progress via Node.js gateway + Redis pub/sub
- **MCP (Model Context Protocol) Server**: Expose research tools to external LLM agents
- **A2A (Agent-to-Agent) Protocol**: Google A2A standard for inter-agent communication with Agent Cards
- **Async Pipeline Execution**: Celery workers for non-blocking research jobs
- **Scheduled Research**: Recurring research jobs (daily/weekly/monthly) via Celery Beat
- **Paper Collections**: User-curated paper collections with bookmarking and notes
- **Export System**: Export reports in Markdown, JSON, CSV formats
- **Analytics Dashboard**: Score distribution charts, classification breakdowns, activity timelines
- **AGI Radar Charts**: Visual 10-axis parameter comparison per paper
- **Swagger/OpenAPI Documentation**: Auto-generated API docs at /api/docs/
- **Docker Compose**: Multi-container orchestration with no port conflicts

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Recharts, Zustand |
| API Gateway | Node.js, Express, WebSocket (ws), Redis pub/sub |
| Backend | Django 5.1, Django REST Framework, PostgreSQL |
| AI/ML | LangChain, LangGraph, OpenAI GPT-4o-mini |
| Task Queue | Celery, Redis, Celery Beat |
| Protocols | MCP (Model Context Protocol), A2A (Agent-to-Agent) |
| Infrastructure | Docker Compose, Nginx, Gunicorn |

## Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY
```

### 2. Launch All Services

```bash
docker compose up --build
```

### 3. Access the Application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3045 |
| API Gateway | http://localhost:3046 |
| Backend API | http://localhost:8045 |
| API Docs (Swagger) | http://localhost:8045/api/docs/ |
| Django Admin | http://localhost:8045/admin/ |

### 4. Create Initial User

```bash
docker compose exec backend python manage.py create_default_user
# Login: admin / admin123
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/token/` - Obtain JWT token
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/me/` - Current user profile

### Research Sessions
- `GET /api/sessions/` - List all sessions
- `POST /api/sessions/` - Launch new research
- `GET /api/sessions/{id}/` - Session detail with papers and logs
- `POST /api/sessions/{id}/cancel/` - Cancel running session
- `POST /api/sessions/{id}/export/` - Export report (json/markdown/csv)

### Papers and Evaluations
- `GET /api/papers/` - List papers (search, filter, bookmark)
- `GET /api/papers/{id}/` - Paper detail with AGI evaluation
- `POST /api/papers/{id}/bookmark/` - Toggle bookmark
- `GET /api/evaluations/` - List all AGI evaluations

### MCP Protocol
- `POST /api/mcp/` - MCP JSON-RPC endpoint (tools/list, tools/call)

### A2A Protocol
- `GET /api/a2a/agents/` - List all agent cards
- `GET/POST /api/a2a/{agent}/` - Agent card or task dispatch

### Dashboard
- `GET /api/dashboard/` - Analytics and statistics

## Multi-Agent Pipeline

```
[User Request]
       |
       v
+------------------+
|      Lead        | --- Orchestrates all phases
|   Supervisor     |     Validates, coordinates, generates final report
+--------+---------+
         |
         v
+------------------+
|    Planner       | --- LLM generates execution plan
|     Agent        |     Keywords, strategy, criteria, focus areas
+--------+---------+
         |
         v
+------------------+
|   Discovery      | --- Searches arXiv with category/date filtering
|   Supervisor     |     Deduplication, validation, statistics
+--------+---------+
         |
         v
+------------------+
|   Evaluation     | --- Scores each paper on 10 AGI parameters
|   Supervisor     |     Weighted scoring, classification, assessment
+--------+---------+
         |
         v
+------------------+
|   Synthesis      | --- Generates comprehensive markdown report
|   and Report     |     Executive summary, rankings, recommendations
+------------------+
```

## AGI Evaluation Parameters

| Parameter | Weight | Description |
|-----------|--------|-------------|
| Novel Problem Solving | 15% | Solving new problems not in training data |
| Few-Shot Learning | 15% | Learning from minimal examples |
| Task Transfer | 15% | Applying skills across domains |
| Abstract Reasoning | 12% | Logical thinking and pattern recognition |
| Contextual Adaptation | 10% | Adapting behavior based on context |
| Multi-Rule Integration | 10% | Following multiple complex rules simultaneously |
| Generalization Efficiency | 8% | Generalizing from small data |
| Meta-Learning | 8% | Learning how to learn |
| World Modeling | 4% | Understanding complex environments |
| Autonomous Goal Setting | 3% | Setting and pursuing own objectives |

## Docker Services

| Service | Port (Host) | Port (Internal) | Purpose |
|---------|-------------|-----------------|---------|
| frontend | 3045 | 80 | React UI (Nginx) |
| gateway | 3046 | 3046 | API Gateway + WebSocket |
| backend | 8045 | 8000 | Django REST API |
| postgres | 5445 | 5432 | PostgreSQL database |
| redis | 6345 | 6379 | Cache + task queue |
| celery-worker | - | - | Async research tasks |
| celery-beat | - | - | Scheduled research jobs |

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Gateway Development
```bash
cd gateway
npm install
npm run dev
```

## License

MIT
