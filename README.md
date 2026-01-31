# AI Research Multi-Agent System

A professional-grade, full-stack application for **autonomous academic research paper discovery and evaluation** powered by a hierarchical multi-agent architecture. The system uses LangChain/LangGraph agents, MCP (Model Context Protocol), and A2A (Agent-to-Agent) protocol to automate the entire research pipeline — from intelligent query planning to paper discovery, AI-powered evaluation, and comprehensive report generation.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [Multi-Agent Pipeline](#multi-agent-pipeline)
- [AGI Evaluation Framework](#agi-evaluation-framework)
- [API Reference](#api-reference)
- [MCP Protocol](#mcp-protocol)
- [A2A Protocol](#a2a-protocol)
- [Frontend Pages](#frontend-pages)
- [Docker Services](#docker-services)
- [WebSocket Real-Time Updates](#websocket-real-time-updates)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     React / TypeScript Frontend                      │
│         Dashboard │ Research │ Papers │ Collections │ Schedule       │
│                         (Port 3045)                                  │
├─────────────────────────────────────────────────────────────────────┤
│                  Node.js API Gateway + WebSocket                     │
│          REST Proxy │ JWT Auth │ Real-time Updates │ Redis Pub/Sub  │
│                         (Port 3046)                                  │
├─────────────────────────────────────────────────────────────────────┤
│                     Django REST API Backend                          │
│   Sessions │ Papers │ Evaluations │ MCP │ A2A │ Collections │ Export│
│                         (Port 8045)                                  │
├──────────────┬──────────────┬───────────────┬───────────────────────┤
│  PostgreSQL  │    Redis     │ Celery Worker │   Celery Beat         │
│   Database   │ Cache/Queue  │  (Async Jobs) │ (Scheduled Research)  │
│  (Port 5445) │ (Port 6345)  │               │                       │
└──────────────┴──────────────┴───────────────┴───────────────────────┘
```

### Request Flow

1. **User** interacts with the React frontend (port 3045)
2. All API requests route through the **Node.js Gateway** (port 3046), which handles JWT authentication, request proxying, and WebSocket connections
3. The gateway forwards REST requests to the **Django Backend** (port 8045)
4. For research sessions, Django dispatches async tasks to **Celery Workers** via **Redis** (port 6345)
5. Celery workers run the multi-agent pipeline (Planner → Discovery → Evaluation → Synthesis)
6. Pipeline progress is published to Redis pub/sub channels
7. The gateway subscribes to Redis and pushes real-time updates to connected WebSocket clients
8. Results are persisted in **PostgreSQL** (port 5445)

---

## Key Features

### Intelligent Research Pipeline
- **AI-Powered Query Planning**: LLM generates optimized ArXiv API queries with AND/OR logic, required terms, and search strategies tailored to the research objective
- **Progressive Discovery Strategy**: Round 1 runs targeted AND-based queries for precision; Round 2 broadens with OR-based keyword queries if more papers are needed
- **Relevance Scoring Engine**: Multi-factor scoring weighing title matches (2x), abstract matches, multi-word phrase bonuses, and required-term gating — ensures only relevant papers pass through
- **ArXiv Paper Discovery**: Searches arXiv with relevance-based sorting, deduplication by title normalization, and abstract validation
- **10-Parameter AGI Evaluation**: Each paper is scored by GPT-4o-mini across 10 weighted dimensions (see [AGI Evaluation Framework](#agi-evaluation-framework))
- **Comprehensive Report Generation**: Markdown reports with executive summaries, ranked papers, score distributions, key findings, and recommendations

### User-Facing Features
- **Analytics Dashboard**: Score distribution charts (Recharts), classification breakdowns (high/medium/low), activity timelines, top papers, and source distribution
- **Paper Collections**: Create named collections, add papers from any session via the paper detail page, remove papers, expand/collapse to browse collection contents
- **Bookmarking & Notes**: Bookmark papers and attach personal notes from the paper detail view
- **AGI Radar Charts**: Interactive 10-axis radar visualization of each paper's evaluation scores
- **Score Gauge**: Color-coded circular gauge showing overall AGI score
- **Export System**: Export session reports in Markdown, JSON, or CSV format
- **Scheduled Research**: Configure recurring research jobs (daily, weekly, monthly) with Celery Beat

### Platform & Protocol Features
- **Full Authentication System**: JWT-based auth with registration, login, token refresh, and user profiles
- **Real-time WebSocket Updates**: Live pipeline progress (phase changes, paper discoveries, evaluation completions) via Node.js gateway + Redis pub/sub
- **MCP (Model Context Protocol) Server**: Expose research tools (`search_papers`, `evaluate_paper`, `get_session_report`) to external LLM agents via JSON-RPC
- **A2A (Agent-to-Agent) Protocol**: Google A2A standard with Agent Cards for inter-agent communication — research_planner, paper_evaluator, and report_generator agents
- **Swagger/OpenAPI Documentation**: Auto-generated interactive API docs at `/api/docs/`
- **Docker Compose Orchestration**: 7 containers with health checks, dependency ordering, and volume persistence

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18, TypeScript, Vite | Single-page application with fast HMR |
| **Styling** | Tailwind CSS, PostCSS | Utility-first CSS framework |
| **Charts** | Recharts | Dashboard analytics and radar charts |
| **State** | Zustand | Lightweight global auth state management |
| **Notifications** | react-hot-toast | Toast notifications for user feedback |
| **Routing** | React Router v6 | Client-side routing with protected routes |
| **Icons** | Lucide React | Consistent icon library |
| **API Gateway** | Node.js, Express | REST proxy, JWT validation, WebSocket hub |
| **WebSocket** | ws (Node.js) | Real-time bidirectional communication |
| **Pub/Sub** | Redis | Cross-service event broadcasting |
| **Backend** | Django 5.1, Django REST Framework | REST API, ORM, admin interface |
| **Database** | PostgreSQL 15 | Relational data storage with UUID primary keys |
| **Cache/Queue** | Redis 7 | Celery broker, result backend, pub/sub |
| **Task Queue** | Celery 5 | Async pipeline execution |
| **Scheduler** | Celery Beat | Periodic/scheduled research jobs |
| **AI/ML** | LangChain, LangGraph | Agent orchestration framework |
| **LLM** | OpenAI GPT-4o-mini | Planning, evaluation, and synthesis |
| **Paper Source** | ArXiv API (via `arxiv` Python package) | Academic paper search and metadata |
| **API Docs** | drf-spectacular (Swagger/OpenAPI) | Auto-generated API documentation |
| **Containerization** | Docker, Docker Compose | Multi-service orchestration |
| **Web Server** | Nginx (frontend), Gunicorn (backend) | Production-grade serving |

---

## Project Structure

```
AI-Research-Agent/
├── docker-compose.yml              # Multi-service orchestration (7 containers)
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
├── architecture.drawio             # Draw.io architecture diagram
├── AI_Research_Agent_Architecture.pptx  # PowerPoint architecture slides
├── generate_pptx.py                # Script to regenerate the PPTX
├── MLS12_AI_Research_Multi_Agent_System.ipynb  # Original research notebook
│
├── backend/                        # Django REST API
│   ├── Dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/                     # Django project configuration
│   │   ├── settings.py             #   Database, Redis, CORS, REST framework settings
│   │   ├── urls.py                 #   Root URL configuration
│   │   ├── celery_app.py           #   Celery configuration with Redis broker
│   │   └── wsgi.py                 #   WSGI entry point for Gunicorn
│   └── research_app/               # Main Django application
│       ├── models.py               #   Database models (Session, Paper, Evaluation, etc.)
│       ├── admin.py                #   Django admin registration
│       ├── tasks.py                #   Celery task definitions
│       ├── agents/                 #   AI Agent modules
│       │   ├── config.py           #     LLM configuration (model, temperature)
│       │   ├── planner.py          #     Research planning agent (generates queries)
│       │   ├── discovery.py        #     ArXiv paper discovery agent
│       │   ├── evaluation.py       #     AGI evaluation agent (10-parameter scoring)
│       │   └── pipeline.py         #     Pipeline orchestrator (progressive discovery)
│       ├── api/                    #   REST API layer
│       │   ├── urls.py             #     URL routing (router + custom endpoints)
│       │   ├── views.py            #     ViewSets and API views
│       │   ├── serializers.py      #     DRF serializers (list, detail, create)
│       │   └── mcp_views.py        #     MCP JSON-RPC endpoint
│       ├── mcp/                    #   Model Context Protocol
│       │   └── server.py           #     MCP tool definitions and handlers
│       ├── a2a/                    #   Agent-to-Agent Protocol
│       │   └── protocol.py         #     A2A agent cards and task dispatch
│       ├── management/commands/    #   Custom manage.py commands
│       │   └── create_default_user.py  # Create admin user for quick start
│       └── migrations/             #   Database migrations
│
├── frontend/                       # React + TypeScript SPA
│   ├── Dockerfile                  #   Multi-stage build (npm ci → nginx)
│   ├── nginx.conf                  #   Nginx config with API proxy rules
│   ├── package.json
│   ├── vite.config.ts              #   Vite dev server config
│   ├── tailwind.config.js          #   Tailwind theme (primary color palette)
│   ├── tsconfig.json
│   ├── index.html                  #   SPA entry point
│   └── src/
│       ├── main.tsx                #   React root with router and toast provider
│       ├── App.tsx                 #   Route definitions and auth guards
│       ├── index.css               #   Tailwind imports and base styles
│       ├── components/             #   Reusable UI components
│       │   ├── Layout.tsx          #     App shell with sidebar navigation
│       │   ├── AGIRadarChart.tsx   #     10-axis radar chart (Recharts)
│       │   ├── ScoreGauge.tsx      #     Circular score gauge with color coding
│       │   └── StatusBadge.tsx     #     Classification badge (high/medium/low)
│       ├── pages/                  #   Route-level page components
│       │   ├── DashboardPage.tsx   #     Analytics dashboard with charts
│       │   ├── NewResearchPage.tsx #     Research session creation form
│       │   ├── SessionsPage.tsx    #     Session list with status indicators
│       │   ├── SessionDetailPage.tsx #   Session detail with papers and logs
│       │   ├── PapersPage.tsx      #     Searchable paper list with filters
│       │   ├── PaperDetailPage.tsx #     Paper detail with evaluation and collections
│       │   ├── CollectionsPage.tsx #     Collection management (CRUD, papers)
│       │   ├── ScheduledPage.tsx   #     Scheduled research management
│       │   ├── LoginPage.tsx       #     JWT login form
│       │   └── RegisterPage.tsx    #     User registration form
│       ├── services/               #   API and WebSocket clients
│       │   ├── api.ts              #     Axios client with JWT interceptors
│       │   └── websocket.ts        #     WebSocket connection manager
│       ├── store/
│       │   └── authStore.ts        #     Zustand auth state (tokens, user)
│       └── types/
│           └── index.ts            #     TypeScript interfaces for all entities
│
├── gateway/                        # Node.js API Gateway
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       └── index.js                #   Express server + WebSocket + Redis pub/sub
│
└── scripts/
    └── init-db.sql                 #   PostgreSQL initialization script
```

---

## Getting Started

### Prerequisites

- **Docker** and **Docker Compose** (v2+)
- **OpenAI API Key** (GPT-4o-mini is used for planning, evaluation, and synthesis)

### Step 1: Clone and Configure

```bash
git clone <repository-url>
cd AI-Research-Agent

# Copy the environment template
cp .env.example .env

# Edit .env and set your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### Step 2: Launch All Services

```bash
docker compose up --build
```

This starts 7 containers: frontend, gateway, backend, postgres, redis, celery-worker, and celery-beat.

### Step 3: Initialize the Database

On first run, Django automatically runs migrations. Create a default admin user:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py create_default_user
```

Default credentials: **admin / admin123**

### Step 4: Access the Application

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3045 | Main application UI |
| **API Gateway** | http://localhost:3046 | REST proxy + WebSocket |
| **Backend API** | http://localhost:8045/api/ | Direct Django REST API |
| **Swagger Docs** | http://localhost:8045/api/docs/ | Interactive API documentation |
| **Django Admin** | http://localhost:8045/admin/ | Database admin interface |

### Step 5: Run Your First Research

1. Log in at http://localhost:3045 with admin/admin123
2. Click **"New Research"** in the sidebar
3. Enter a research objective, e.g.: *"Find recent papers on reinforcement learning for stock trading"*
4. Configure max papers (1-50) and lookback days (1-365)
5. Optionally add custom keywords and ArXiv categories
6. Click **"Start Research"** and watch real-time progress via WebSocket

---

## Configuration

### Environment Variables (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | OpenAI API key for GPT-4o-mini |
| `POSTGRES_DB` | `ai_research` | PostgreSQL database name |
| `POSTGRES_USER` | `research_user` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `research_pass` | PostgreSQL password |
| `DJANGO_SECRET_KEY` | *(auto-generated)* | Django secret key |
| `DJANGO_DEBUG` | `1` | Debug mode (0 for production) |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection URL |
| `GATEWAY_PORT` | `3046` | Node.js gateway port |
| `BACKEND_PORT` | `8045` | Django backend port |
| `FRONTEND_PORT` | `3045` | Frontend (Nginx) port |

### LLM Configuration

The LLM model and parameters are configured in `backend/research_app/agents/config.py`:

```python
LLM_MODEL = "gpt-4o-mini"      # OpenAI model for all agents
LLM_TEMPERATURE = 0.3           # Lower = more deterministic
```

---

## Usage Guide

### Running a Research Session

1. Navigate to **New Research** page
2. Enter your research objective in natural language
3. The system will:
   - **Plan**: Generate optimized ArXiv queries and search strategy
   - **Discover**: Search ArXiv with progressive query strategy, filter by relevance
   - **Evaluate**: Score each paper across 10 AGI dimensions using GPT-4o-mini
   - **Synthesize**: Generate a comprehensive markdown report
4. View results on the **Session Detail** page with papers, scores, and the full report

### Managing Papers

- **Browse**: The Papers page shows all discovered papers across sessions with search and bookmark filters
- **Detail View**: Click any paper to see its abstract, AGI evaluation radar chart, parameter scores, key innovations, and limitations
- **Bookmark**: Click the bookmark icon to save papers for quick access
- **Notes**: Add personal notes to any paper from the detail page

### Using Collections

1. Go to the **Collections** page and click **"New Collection"**
2. Give it a name and optional description
3. Navigate to any paper's detail page
4. Click the **folder icon** (FolderPlus) in the top-right
5. Select a collection from the dropdown to add the paper
6. Back on the Collections page, click any collection to expand and see its papers
7. Remove papers with the X button, or delete entire collections with the trash icon

### Scheduling Recurring Research

1. Go to the **Scheduled** page
2. Create a new schedule with a research objective and frequency (daily/weekly/monthly)
3. Celery Beat will automatically trigger research sessions at the configured intervals
4. View past runs and results from the scheduled research detail

### Exporting Reports

From any session detail page, use the export button to download reports in:
- **Markdown**: Full formatted report with tables and sections
- **JSON**: Structured data for programmatic access
- **CSV**: Tabular paper data for spreadsheet analysis

---

## Multi-Agent Pipeline

The research pipeline is orchestrated by a hierarchy of specialized agents:

```
[User: "Find papers on reinforcement learning for stock trading"]
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  PHASE 1: PLANNING                                        │
│  ┌─────────────────────────────────────────────────┐      │
│  │ Planner Agent (GPT-4o-mini)                     │      │
│  │ • Extracts key concepts from research objective  │      │
│  │ • Generates ArXiv API queries with AND logic     │      │
│  │ • Identifies required terms for relevance gating │      │
│  │ • Suggests ArXiv categories and date ranges      │      │
│  │ • Outputs: keywords, arxiv_queries, strategy     │      │
│  └─────────────────────────────────────────────────┘      │
│  Output example:                                          │
│  arxiv_queries: [                                         │
│    'all:"reinforcement learning" AND all:"stock trading"',│
│    'abs:"deep RL" AND abs:"financial markets"'            │
│  ]                                                        │
│  required_terms: ["reinforcement", "trading"]             │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  PHASE 2: DISCOVERY (Progressive Strategy)                │
│                                                           │
│  Round 1 — Targeted Queries (no date/category filters):   │
│  ┌─────────────────────────────────────────────────┐      │
│  │ For each arxiv_query from planner:              │      │
│  │ • Search ArXiv API sorted by Relevance          │      │
│  │ • Fetch 3x requested papers for filtering room  │      │
│  │ • Deduplicate by normalized title               │      │
│  └─────────────────────────────────────────────────┘      │
│                                                           │
│  Round 2 — Broad Fallback (if < max_papers found):        │
│  ┌─────────────────────────────────────────────────┐      │
│  │ • Build OR-based query from all keywords        │      │
│  │ • Apply date range and category filters          │      │
│  │ • Fill remaining slots                           │      │
│  └─────────────────────────────────────────────────┘      │
│                                                           │
│  Relevance Filter:                                        │
│  ┌─────────────────────────────────────────────────┐      │
│  │ • Extract terms from objective (multi-word first)│      │
│  │ • Score: title match (2x) + abstract match (1x)  │      │
│  │ • Multi-word phrases weighted by word count       │      │
│  │ • Required terms gate (score=0 if missing)        │      │
│  │ • Minimum score threshold: 2.0                    │      │
│  │ • Sort by relevance score, take top max_papers    │      │
│  └─────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  PHASE 3: EVALUATION                                      │
│  ┌─────────────────────────────────────────────────┐      │
│  │ Evaluation Agent (GPT-4o-mini) per paper:       │      │
│  │ • Reads title + abstract                         │      │
│  │ • Scores 10 AGI parameters (0-10 each)           │      │
│  │ • Applies weighted formula → agi_score (0-100)   │      │
│  │ • Classifies: high (≥70), medium (≥40), low (<40)│      │
│  │ • Extracts: key innovations, limitations          │      │
│  │ • Writes: overall assessment, confidence level    │      │
│  └─────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  PHASE 4: SYNTHESIS & REPORT                              │
│  ┌─────────────────────────────────────────────────┐      │
│  │ • Ranks papers by AGI score                      │      │
│  │ • Generates executive summary                    │      │
│  │ • Score distribution analysis                    │      │
│  │ • Top papers with key findings                   │      │
│  │ • Research recommendations                       │      │
│  │ • Full markdown report output                    │      │
│  └─────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────┘
```

### Pipeline Configuration

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `max_papers` | 1-50 | 10 | Maximum papers to evaluate |
| `days_lookback` | 1-365 | 14 | Date range for paper search |
| `custom_keywords` | list | [] | Additional search keywords |
| `search_categories` | list | [] | ArXiv category filters (e.g., cs.AI, q-fin.TR) |

---

## AGI Evaluation Framework

Each paper is evaluated across 10 parameters with weighted scoring:

| # | Parameter | Weight | Score Range | What It Measures |
|---|-----------|--------|-------------|-----------------|
| 1 | **Novel Problem Solving** | 15% | 0-10 | Ability to solve new problems not present in training data |
| 2 | **Few-Shot Learning** | 15% | 0-10 | Learning effectively from very few examples |
| 3 | **Task Transfer** | 15% | 0-10 | Applying learned skills across different domains |
| 4 | **Abstract Reasoning** | 12% | 0-10 | Logical thinking, pattern recognition, abstract concept manipulation |
| 5 | **Contextual Adaptation** | 10% | 0-10 | Adapting behavior based on environmental/situational context |
| 6 | **Multi-Rule Integration** | 10% | 0-10 | Following and integrating multiple complex rules simultaneously |
| 7 | **Generalization Efficiency** | 8% | 0-10 | Generalizing effectively from limited training data |
| 8 | **Meta-Learning** | 8% | 0-10 | Learning how to learn — improving the learning process itself |
| 9 | **World Modeling** | 4% | 0-10 | Understanding and modeling complex real-world environments |
| 10 | **Autonomous Goal Setting** | 3% | 0-10 | Independently setting and pursuing meaningful objectives |

### Classification Thresholds

| Classification | AGI Score | Color | Description |
|---------------|-----------|-------|-------------|
| **High** | >= 70 | Green | Strong AGI relevance — significant advances |
| **Medium** | >= 40 | Yellow | Moderate AGI relevance — partial contributions |
| **Low** | < 40 | Red | Limited AGI relevance — tangential or foundational |

### Score Formula

```
agi_score = (novel_problem_solving × 0.15) + (few_shot_learning × 0.15) +
            (task_transfer × 0.15) + (abstract_reasoning × 0.12) +
            (contextual_adaptation × 0.10) + (multi_rule_integration × 0.10) +
            (generalization_efficiency × 0.08) + (meta_learning × 0.08) +
            (world_modeling × 0.04) + (autonomous_goal_setting × 0.03)

# Scaled to 0-100
final_score = agi_score × 10
```

---

## API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register/` | Register a new user |
| `POST` | `/api/auth/token/` | Obtain JWT access + refresh tokens |
| `POST` | `/api/auth/token/refresh/` | Refresh expired access token |
| `GET` | `/api/auth/me/` | Get current user profile |

### Research Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/sessions/` | List all research sessions |
| `POST` | `/api/sessions/` | Create and launch a new research session |
| `GET` | `/api/sessions/{id}/` | Session detail with papers, evaluations, and agent logs |
| `POST` | `/api/sessions/{id}/cancel/` | Cancel a running session |
| `POST` | `/api/sessions/{id}/export/` | Export session report (format: json, markdown, csv) |

#### Create Session Request Body

```json
{
  "research_objective": "Find recent papers on reinforcement learning for stock trading",
  "title": "RL Stock Trading Research",
  "max_papers": 10,
  "days_lookback": 30,
  "custom_keywords": ["algorithmic trading", "deep RL"],
  "search_categories": ["cs.AI", "q-fin.TR"]
}
```

### Papers

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/papers/` | List papers (supports `?search=`, `?is_bookmarked=true`) |
| `GET` | `/api/papers/{id}/` | Paper detail with full AGI evaluation |
| `POST` | `/api/papers/{id}/bookmark/` | Toggle bookmark status |
| `PATCH` | `/api/papers/{id}/notes/` | Update user notes |

### AGI Evaluations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/evaluations/` | List all evaluations with scores |

### Collections

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/collections/` | List user's collections |
| `POST` | `/api/collections/` | Create a new collection |
| `GET` | `/api/collections/{id}/` | Collection detail with nested papers |
| `PUT` | `/api/collections/{id}/` | Update collection name/description |
| `DELETE` | `/api/collections/{id}/` | Delete a collection (papers are preserved) |
| `POST` | `/api/collections/{id}/add_paper/` | Add a paper to the collection |
| `POST` | `/api/collections/{id}/remove_paper/` | Remove a paper from the collection |

### Scheduled Research

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/scheduled/` | List scheduled research jobs |
| `POST` | `/api/scheduled/` | Create a new scheduled job |
| `PATCH` | `/api/scheduled/{id}/` | Update schedule (activate/deactivate) |
| `DELETE` | `/api/scheduled/{id}/` | Delete a scheduled job |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/dashboard/` | Analytics: totals, distributions, recent sessions, top papers |

---

## MCP Protocol

The Model Context Protocol (MCP) endpoint allows external LLM agents to use this system's research capabilities as tools.

**Endpoint**: `POST /api/mcp/`

### Available Tools

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `search_papers` | Search for papers by query | `query`, `max_results` |
| `evaluate_paper` | Evaluate a paper's AGI relevance | `paper_id` |
| `get_session_report` | Get the final report for a session | `session_id` |

### Example MCP Request

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "search_papers",
    "arguments": {
      "query": "transformer architecture improvements",
      "max_results": 5
    }
  }
}
```

---

## A2A Protocol

The Agent-to-Agent (A2A) protocol implements the Google A2A standard, enabling inter-agent communication with structured Agent Cards.

**Endpoints**:
- `GET /api/a2a/agents/` — List all available agent cards
- `GET /api/a2a/{agent_name}/` — Get a specific agent card
- `POST /api/a2a/{agent_name}/` — Dispatch a task to an agent

### Available Agents

| Agent | Skills | Description |
|-------|--------|-------------|
| `research_planner` | Query planning, keyword extraction | Plans research strategy from objectives |
| `paper_evaluator` | AGI scoring, classification | Evaluates papers on 10 AGI parameters |
| `report_generator` | Synthesis, markdown generation | Generates comprehensive research reports |

---

## Frontend Pages

| Page | Route | Description |
|------|-------|-------------|
| **Dashboard** | `/` | Analytics overview with charts showing score distributions, classification breakdowns, papers by source, and session timelines |
| **New Research** | `/research/new` | Form to create a new research session with objective, keywords, categories, and configuration |
| **Sessions** | `/sessions` | List of all research sessions with status badges, paper counts, and avg scores |
| **Session Detail** | `/sessions/:id` | Detailed view with paper list, agent execution logs, and the synthesized report |
| **Papers** | `/papers` | Searchable, filterable list of all discovered papers with bookmark toggles |
| **Paper Detail** | `/papers/:id` | Full paper view with abstract, AGI radar chart, parameter scores, innovations/limitations, notes, and collection management |
| **Collections** | `/collections` | Create/delete collections, expand to browse papers, remove papers from collections |
| **Scheduled** | `/scheduled` | Manage recurring research jobs with frequency and activation controls |
| **Login** | `/login` | JWT authentication form |
| **Register** | `/register` | New user registration form |

---

## Docker Services

| Service | Image | Port (Host→Container) | Purpose |
|---------|-------|----------------------|---------|
| `frontend` | Node → Nginx | 3045 → 80 | React SPA served by Nginx with API proxy rules |
| `gateway` | Node.js 20 | 3046 → 3046 | Express API gateway + WebSocket server + Redis pub/sub |
| `backend` | Python 3.11 | 8045 → 8000 | Django REST API served by Gunicorn (4 workers) |
| `postgres` | PostgreSQL 15 | 5445 → 5432 | Relational database with persistent volume |
| `redis` | Redis 7 Alpine | 6345 → 6379 | Task broker, result backend, pub/sub messaging |
| `celery-worker` | Python 3.11 | — | Async research pipeline execution |
| `celery-beat` | Python 3.11 | — | Periodic task scheduler for recurring research |

### Docker Compose Commands

```bash
# Start all services
docker compose up --build

# Start in background
docker compose up -d --build

# View logs
docker compose logs -f backend
docker compose logs -f celery-worker

# Run migrations
docker compose exec backend python manage.py migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser

# Stop all services
docker compose down

# Stop and remove volumes (full reset)
docker compose down -v
```

---

## WebSocket Real-Time Updates

The gateway provides WebSocket connections for real-time pipeline monitoring.

### Connection

```javascript
const ws = new WebSocket('ws://localhost:3046/ws?token=<jwt-access-token>');
```

### Message Types

```json
// Phase change
{
  "type": "phase_change",
  "session_id": "uuid",
  "phase": "evaluation",
  "message": "Evaluating papers..."
}

// Paper discovered
{
  "type": "paper_discovered",
  "session_id": "uuid",
  "paper": { "title": "...", "source": "arxiv" }
}

// Session completed
{
  "type": "session_completed",
  "session_id": "uuid",
  "status": "completed"
}
```

---

## Development

### Backend Development (without Docker)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=sk-your-key
export DATABASE_URL=postgres://user:pass@localhost:5432/ai_research
export REDIS_URL=redis://localhost:6379/0

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver 0.0.0.0:8045

# Start Celery worker (separate terminal)
celery -A config.celery_app worker -l info

# Start Celery beat (separate terminal)
celery -A config.celery_app beat -l info
```

### Frontend Development (without Docker)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server with HMR
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Gateway Development (without Docker)

```bash
cd gateway

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## Troubleshooting

### Common Issues

**Papers returned are not relevant to my query**
- Use specific, descriptive terms in your research objective (e.g., "reinforcement learning for stock trading" instead of "stock trading AI")
- Add custom keywords to narrow the search
- The progressive discovery strategy prioritizes precision in Round 1; if results are too broad, the relevance filter (minimum score 2.0) removes off-topic papers

**Zero papers returned**
- Try broadening your search terms — very niche queries may not have recent ArXiv papers
- Increase `days_lookback` to search a wider date range
- Remove category filters to search across all ArXiv categories

**WebSocket connection fails**
- Ensure the gateway service is running on port 3046
- Check that your JWT token is valid and not expired
- Verify Redis is running (WebSocket events are published via Redis pub/sub)

**Celery tasks stuck in pending**
- Check Redis connectivity: `docker compose exec redis redis-cli ping`
- Check Celery worker logs: `docker compose logs celery-worker`
- Ensure `OPENAI_API_KEY` is set correctly in the environment

**Database migration errors**
- Run `docker compose exec backend python manage.py migrate` after code changes
- For a full reset: `docker compose down -v && docker compose up --build`

**Frontend build errors**
- Clear node_modules: `rm -rf frontend/node_modules && cd frontend && npm ci`
- Check TypeScript errors: `cd frontend && npx tsc --noEmit`

**Docker build fails**
- Ensure Docker has sufficient memory (at least 4GB recommended)
- Clean build cache: `docker compose build --no-cache`
- Check that all Dockerfiles have correct base images

---

## License

MIT
