"""
Planner Agent - Creates execution plans for research objectives.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .config import get_config
from .evaluation import call_llm_with_retry

logger = logging.getLogger("research_app.agents.planner")

PLANNER_SYSTEM_PROMPT = """You are a Planning Specialist in an Artificial General Intelligence research system.

Create a comprehensive research execution plan based on the given objective.

OUTPUT FORMAT: Return a valid JSON object:
{
    "search_keywords": ["keyword1", "keyword2", ...],
    "search_strategy": {
        "primary_sources": ["arxiv"],
        "categories": ["cs.AI", "cs.LG", "cs.CL"],
        "date_range": "YYYY-MM-DD to YYYY-MM-DD",
        "max_papers_per_source": 10
    },
    "success_criteria": {
        "min_papers": 10,
        "min_high_agi_papers": 2,
        "quality_threshold": 0.7
    },
    "focus_areas": ["specific area 1", "specific area 2"],
    "exclusions": ["topics to avoid"],
    "special_instructions": "Any specific guidance"
}

GUIDELINES:
1. Extract 5-10 highly relevant search keywords
2. Set appropriate time windows
3. Define measurable success criteria
4. Focus on 2-5 specific research areas
5. List topics that should be avoided

Be thorough, specific, and actionable."""


def create_execution_plan(research_objective: str, days_lookback: int = 14) -> Dict[str, Any]:
    """Create an execution plan for the research objective."""
    config = get_config()
    llm = ChatOpenAI(model_name=config.openai_model_name, temperature=0.2)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_lookback)
    date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

    user_prompt = f"""Create a detailed execution plan for:

RESEARCH OBJECTIVE: {research_objective}

Current date: {datetime.now().isoformat()}
Default date range: {date_range}

Context:
- AGI-focused research system
- Access to arXiv database
- Pipeline: discovery → evaluation → synthesis
- Focus on recent, high-impact AI/ML work

Generate the execution plan now."""

    try:
        response = call_llm_with_retry(
            llm,
            [SystemMessage(content=PLANNER_SYSTEM_PROMPT), HumanMessage(content=user_prompt)],
        )

        content = response.content
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            content = content[json_start:json_end]

        plan = json.loads(content.strip())

        if not plan.get("search_strategy", {}).get("date_range"):
            plan.setdefault("search_strategy", {})["date_range"] = date_range

        logger.info(f"Execution plan created: {len(plan.get('search_keywords', []))} keywords")
        return plan

    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Plan creation failed: {e}, using default plan")
        return {
            "search_keywords": ["AGI", "artificial general intelligence", "general AI"],
            "search_strategy": {
                "primary_sources": ["arxiv"],
                "categories": ["cs.AI", "cs.LG"],
                "date_range": date_range,
                "max_papers_per_source": 10,
            },
            "success_criteria": {"min_papers": 10, "min_high_agi_papers": 2},
            "focus_areas": ["general artificial intelligence"],
            "exclusions": [],
            "special_instructions": f"Default plan for: {research_objective}",
        }
