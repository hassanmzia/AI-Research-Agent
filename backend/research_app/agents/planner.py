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

PLANNER_SYSTEM_PROMPT = """You are a Research Planning Specialist that creates execution plans for academic paper searches on arXiv.

Create a comprehensive research execution plan based on the given objective. The plan must be highly relevant to the user's specific research topic.

OUTPUT FORMAT: Return a valid JSON object:
{
    "search_keywords": ["keyword phrase 1", "keyword phrase 2", ...],
    "arxiv_queries": [
        "all:\\\"reinforcement learning\\\" AND all:\\\"stock trading\\\"",
        "abs:\\\"algorithmic trading\\\" AND abs:\\\"deep reinforcement learning\\\""
    ],
    "search_strategy": {
        "primary_sources": ["arxiv"],
        "categories": ["q-fin.TR", "q-fin.PM", "cs.AI"],
        "date_range": "YYYY-MM-DD to YYYY-MM-DD",
        "max_papers_per_source": 10
    },
    "required_terms": ["term1", "term2"],
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
1. Extract 5-10 highly relevant search keyword PHRASES (not single words) that directly match the research objective. E.g. for stock trading with RL, use phrases like "stock trading", "reinforcement learning", "algorithmic trading", "portfolio optimization".
2. Generate 2-4 arxiv_queries using arXiv query syntax. These are the actual queries sent to arXiv's API.
   - Use AND between core concepts to ensure papers match ALL key aspects.
   - Use field prefixes: all: (title+abstract+fulltext), abs: (abstract), ti: (title)
   - Quote multi-word phrases: all:\"reinforcement learning\" AND all:\"stock trading\"
   - Good: all:\"stock trading\" AND all:\"reinforcement learning\"
   - Bad: stock OR trading OR reinforcement OR learning (too broad, matches anything)
3. Set required_terms: 2-3 terms that a relevant paper MUST mention in its title or abstract. Papers missing ALL required terms will be filtered out.
4. Choose arXiv categories relevant to the topic (q-fin.* for finance, cs.* for CS, stat.* for statistics, econ.* for economics, etc.). Use an empty list if the topic is broad.
5. Set appropriate time windows
6. Focus on 2-5 specific research areas directly related to the objective

IMPORTANT: Keywords, queries, and categories MUST be directly relevant to the user's research objective. Do not default to AI/AGI topics unless the user specifically asks about AI/AGI.

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
- Access to arXiv database
- Pipeline: discovery → evaluation → synthesis
- Focus on papers directly relevant to the research objective above

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
        logger.error(f"Plan creation failed: {e}, using default plan derived from objective")
        # Derive keywords from the research objective itself
        fallback_keywords = [
            kw.strip() for kw in research_objective.split()
            if len(kw.strip()) > 3
        ][:8]
        if not fallback_keywords:
            fallback_keywords = [research_objective[:100]]
        return {
            "search_keywords": fallback_keywords,
            "search_strategy": {
                "primary_sources": ["arxiv"],
                "categories": [],
                "date_range": date_range,
                "max_papers_per_source": 10,
            },
            "success_criteria": {"min_papers": 10, "min_high_agi_papers": 2},
            "focus_areas": [research_objective[:200]],
            "exclusions": [],
            "special_instructions": f"Default plan for: {research_objective}",
        }
