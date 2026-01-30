"""
MCP (Model Context Protocol) Server for the AI Research System.

Exposes research tools via MCP protocol so that external AI agents and
LLM-based applications can invoke them as tool calls.

Tools exposed:
  - search_papers: Search arXiv for research papers
  - evaluate_paper: Evaluate a paper against AGI parameters
  - create_research_plan: Generate execution plan for a research objective
  - get_session_report: Retrieve a session's final report
  - get_agi_leaderboard: Get top-scored papers across all sessions
"""
import json
import logging
from typing import Any

logger = logging.getLogger("research_app.mcp")


class MCPToolRegistry:
    """Registry that holds MCP-compatible tool definitions."""

    def __init__(self):
        self.tools = {}

    def register(self, name: str, description: str, parameters: dict, handler):
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "handler": handler,
        }

    def list_tools(self):
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "inputSchema": {
                    "type": "object",
                    "properties": t["parameters"],
                },
            }
            for t in self.tools.values()
        ]

    def call_tool(self, name: str, arguments: dict) -> Any:
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")
        return self.tools[name]["handler"](**arguments)


# Global registry
registry = MCPToolRegistry()


def _search_papers_handler(query: str, max_papers: int = 10, from_date: str = None, to_date: str = None):
    from research_app.agents.discovery import discover_and_process_papers
    return discover_and_process_papers(query, max_papers, from_date, to_date)


def _evaluate_paper_handler(title: str, abstract: str, authors: list = None):
    from research_app.agents.evaluation import evaluate_paper
    paper = {
        "id": "mcp-manual",
        "title": title,
        "link": "",
        "metadata": {
            "abstract": abstract,
            "authors": [{"name": a} for a in (authors or [])],
            "source": "manual",
        },
    }
    return evaluate_paper(paper)


def _create_plan_handler(research_objective: str, days_lookback: int = 14):
    from research_app.agents.planner import create_execution_plan
    return create_execution_plan(research_objective, days_lookback)


def _get_session_report_handler(session_id: str):
    import django
    django.setup()
    from research_app.models import ResearchSession
    try:
        session = ResearchSession.objects.get(id=session_id)
        return {
            "session_id": str(session.id),
            "status": session.status,
            "report": session.final_report,
            "stats": {
                "papers_discovered": session.total_papers_discovered,
                "papers_evaluated": session.total_papers_evaluated,
                "avg_agi_score": session.avg_agi_score,
            },
        }
    except ResearchSession.DoesNotExist:
        return {"error": f"Session {session_id} not found"}


def _get_leaderboard_handler(limit: int = 20):
    import django
    django.setup()
    from research_app.models import AGIEvaluation
    evaluations = AGIEvaluation.objects.select_related("paper").order_by("-agi_score")[:limit]
    return [
        {
            "paper_title": e.paper.title,
            "agi_score": e.agi_score,
            "classification": e.classification,
            "source": e.paper.source,
            "url": e.paper.url,
        }
        for e in evaluations
    ]


# Register all tools
registry.register(
    "search_papers",
    "Search arXiv for AI/ML research papers with optional date filtering",
    {
        "query": {"type": "string", "description": "Search query"},
        "max_papers": {"type": "integer", "description": "Maximum papers to return"},
        "from_date": {"type": "string", "description": "Start date YYYY-MM-DD"},
        "to_date": {"type": "string", "description": "End date YYYY-MM-DD"},
    },
    _search_papers_handler,
)

registry.register(
    "evaluate_paper",
    "Evaluate a research paper against the 10-parameter AGI framework",
    {
        "title": {"type": "string", "description": "Paper title"},
        "abstract": {"type": "string", "description": "Paper abstract"},
        "authors": {"type": "array", "items": {"type": "string"}, "description": "Author names"},
    },
    _evaluate_paper_handler,
)

registry.register(
    "create_research_plan",
    "Generate an execution plan for a research objective",
    {
        "research_objective": {"type": "string", "description": "The research question"},
        "days_lookback": {"type": "integer", "description": "Days to look back"},
    },
    _create_plan_handler,
)

registry.register(
    "get_session_report",
    "Retrieve the final report for a research session",
    {"session_id": {"type": "string", "description": "Session UUID"}},
    _get_session_report_handler,
)

registry.register(
    "get_agi_leaderboard",
    "Get top-scored papers across all research sessions",
    {"limit": {"type": "integer", "description": "Number of top papers to return"}},
    _get_leaderboard_handler,
)


def handle_mcp_request(request_body: dict) -> dict:
    """Handle an incoming MCP JSON-RPC request."""
    method = request_body.get("method", "")
    params = request_body.get("params", {})
    req_id = request_body.get("id")

    try:
        if method == "tools/list":
            result = registry.list_tools()
        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            result = registry.call_tool(tool_name, arguments)
        elif method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "ai-research-mcp-server",
                    "version": "1.0.0",
                },
                "capabilities": {"tools": {}},
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"},
            }

        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    except Exception as e:
        logger.error(f"MCP request error: {e}")
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32000, "message": str(e)},
        }
