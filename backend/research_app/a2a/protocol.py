"""
A2A (Agent-to-Agent) Protocol Implementation.

Implements the Google A2A protocol for inter-agent communication.
Each agent advertises its capabilities via an Agent Card and can
send/receive tasks to other agents.

Agent Cards:
  - PlannerAgent: Creates research execution plans
  - DiscoveryAgent: Discovers and retrieves papers from academic sources
  - EvaluationAgent: Evaluates papers using the AGI framework
  - SynthesisAgent: Generates comprehensive reports from evaluations
"""
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger("research_app.a2a")


class TaskState(Enum):
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


@dataclass
class AgentCard:
    """A2A Agent Card describing an agent's capabilities."""
    name: str
    description: str
    url: str
    version: str = "1.0.0"
    capabilities: Dict[str, Any] = field(default_factory=dict)
    skills: List[Dict[str, str]] = field(default_factory=list)
    default_input_modes: List[str] = field(default_factory=lambda: ["text/plain"])
    default_output_modes: List[str] = field(default_factory=lambda: ["text/plain", "application/json"])

    def to_dict(self):
        return asdict(self)


@dataclass
class A2ATask:
    """An A2A task exchanged between agents."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    status: str = TaskState.SUBMITTED.value
    messages: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return asdict(self)


class A2AAgentBase:
    """Base class for A2A agents."""

    def __init__(self, card: AgentCard):
        self.card = card
        self.tasks: Dict[str, A2ATask] = {}

    def get_agent_card(self) -> Dict[str, Any]:
        return self.card.to_dict()

    def send_task(self, task_data: Dict[str, Any]) -> A2ATask:
        task = A2ATask(
            session_id=task_data.get("sessionId"),
            messages=task_data.get("message", {}).get("parts", []),
            metadata=task_data.get("metadata", {}),
        )
        self.tasks[task.id] = task
        return self._process_task(task)

    def get_task(self, task_id: str) -> Optional[A2ATask]:
        return self.tasks.get(task_id)

    def cancel_task(self, task_id: str) -> Optional[A2ATask]:
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskState.CANCELED.value
        return task

    def _process_task(self, task: A2ATask) -> A2ATask:
        raise NotImplementedError


class PlannerA2AAgent(A2AAgentBase):
    """A2A Planner Agent."""

    def __init__(self):
        super().__init__(AgentCard(
            name="ResearchPlanner",
            description="Creates comprehensive research execution plans for AGI paper discovery",
            url="/a2a/planner",
            capabilities={"streaming": False, "pushNotifications": False},
            skills=[{
                "id": "create_plan",
                "name": "Create Research Plan",
                "description": "Generates an execution plan with keywords, strategies, and criteria",
            }],
        ))

    def _process_task(self, task: A2ATask) -> A2ATask:
        task.status = TaskState.WORKING.value
        try:
            from research_app.agents.planner import create_execution_plan
            objective = ""
            for msg in task.messages:
                if isinstance(msg, dict) and msg.get("type") == "text":
                    objective = msg.get("text", "")
                    break

            plan = create_execution_plan(objective or "General AGI research")
            task.artifacts.append({
                "name": "execution_plan",
                "parts": [{"type": "application/json", "data": json.dumps(plan)}],
            })
            task.status = TaskState.COMPLETED.value
        except Exception as e:
            task.status = TaskState.FAILED.value
            task.metadata["error"] = str(e)
        return task


class DiscoveryA2AAgent(A2AAgentBase):
    """A2A Discovery Agent."""

    def __init__(self):
        super().__init__(AgentCard(
            name="PaperDiscovery",
            description="Discovers and processes research papers from arXiv and other sources",
            url="/a2a/discovery",
            capabilities={"streaming": False, "pushNotifications": False},
            skills=[{
                "id": "discover_papers",
                "name": "Discover Papers",
                "description": "Search, deduplicate, and validate academic papers",
            }],
        ))

    def _process_task(self, task: A2ATask) -> A2ATask:
        task.status = TaskState.WORKING.value
        try:
            from research_app.agents.discovery import discover_and_process_papers
            params = task.metadata.get("params", {})
            result = discover_and_process_papers(
                query=params.get("query", "artificial general intelligence"),
                max_papers=params.get("max_papers", 10),
                from_date=params.get("from_date"),
                to_date=params.get("to_date"),
            )
            task.artifacts.append({
                "name": "discovery_result",
                "parts": [{"type": "application/json", "data": json.dumps(result, default=str)}],
            })
            task.status = TaskState.COMPLETED.value
        except Exception as e:
            task.status = TaskState.FAILED.value
            task.metadata["error"] = str(e)
        return task


class EvaluationA2AAgent(A2AAgentBase):
    """A2A Evaluation Agent."""

    def __init__(self):
        super().__init__(AgentCard(
            name="AGIEvaluator",
            description="Evaluates research papers using the 10-parameter AGI framework",
            url="/a2a/evaluation",
            capabilities={"streaming": False, "pushNotifications": False},
            skills=[{
                "id": "evaluate_paper",
                "name": "Evaluate Paper for AGI",
                "description": "Scores a paper on 10 AGI parameters with weighted scoring",
            }],
        ))

    def _process_task(self, task: A2ATask) -> A2ATask:
        task.status = TaskState.WORKING.value
        try:
            from research_app.agents.evaluation import evaluate_paper
            paper_data = task.metadata.get("paper", {})
            result = evaluate_paper(paper_data)
            task.artifacts.append({
                "name": "evaluation_result",
                "parts": [{"type": "application/json", "data": json.dumps(result, default=str)}],
            })
            task.status = TaskState.COMPLETED.value
        except Exception as e:
            task.status = TaskState.FAILED.value
            task.metadata["error"] = str(e)
        return task


# Agent registry
_agents = {
    "planner": PlannerA2AAgent(),
    "discovery": DiscoveryA2AAgent(),
    "evaluation": EvaluationA2AAgent(),
}


def get_agent_cards() -> List[Dict[str, Any]]:
    return [agent.get_agent_card() for agent in _agents.values()]


def handle_a2a_request(agent_name: str, method: str, data: dict) -> dict:
    """Handle an A2A protocol request."""
    agent = _agents.get(agent_name)
    if not agent:
        return {"error": f"Unknown agent: {agent_name}"}

    if method == "agent_card":
        return agent.get_agent_card()
    elif method == "tasks/send":
        task = agent.send_task(data)
        return task.to_dict()
    elif method == "tasks/get":
        task = agent.get_task(data.get("id", ""))
        return task.to_dict() if task else {"error": "Task not found"}
    elif method == "tasks/cancel":
        task = agent.cancel_task(data.get("id", ""))
        return task.to_dict() if task else {"error": "Task not found"}
    else:
        return {"error": f"Unknown method: {method}"}
