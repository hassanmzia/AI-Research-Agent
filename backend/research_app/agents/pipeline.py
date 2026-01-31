"""
Research Pipeline - Orchestrates the multi-agent workflow.
Implements the LangGraph-style state machine from the notebook.
"""
import logging
import re
import time
from datetime import datetime
from typing import Dict, Any, List, Callable
from enum import Enum

from .config import get_config
from .planner import create_execution_plan
from .discovery import discover_and_process_papers
from .evaluation import evaluate_paper

logger = logging.getLogger("research_app.agents.pipeline")


class ResearchPhase(Enum):
    INITIALIZATION = "initialization"
    PLANNING = "planning"
    DISCOVERY = "discovery"
    EVALUATION = "evaluation"
    SYNTHESIS = "synthesis"
    COMPLETION = "completion"


def run_pipeline(
    research_objective: str,
    max_papers: int = 10,
    days_lookback: int = 14,
    custom_keywords: List[str] = None,
    search_categories: List[str] = None,
    on_phase_change: Callable = None,
    on_log: Callable = None,
) -> Dict[str, Any]:
    """
    Run the complete multi-agent research pipeline.

    Args:
        research_objective: The research question/objective
        max_papers: Maximum papers to discover
        days_lookback: How many days back to search
        custom_keywords: Optional user-provided search keywords
        on_phase_change: Callback when phase changes
        on_log: Callback for agent log messages

    Returns:
        Complete pipeline result dictionary
    """
    start_time = time.time()

    def log(agent_role: str, message: str, level: str = "info", **kwargs):
        logger.info(f"[{agent_role}] {message}")
        if on_log:
            on_log(agent_role=agent_role, message=message, level=level, metadata=kwargs)

    def change_phase(new_phase: ResearchPhase):
        if on_phase_change:
            on_phase_change(new_phase.value)
        log("lead_supervisor", f"Phase transition → {new_phase.value}")

    result = {
        "phases_completed": [],
        "discovered_papers": [],
        "evaluation_results": [],
        "execution_plan": None,
        "final_report": "",
        "statistics": {},
        "errors": [],
    }

    try:
        # === PHASE 1: PLANNING ===
        change_phase(ResearchPhase.PLANNING)
        log("planner", f"Creating execution plan for: {research_objective}")

        plan = create_execution_plan(research_objective, days_lookback)
        result["execution_plan"] = plan

        # Merge custom keywords
        if custom_keywords:
            plan["search_keywords"] = list(
                set(plan.get("search_keywords", []) + custom_keywords)
            )

        result["phases_completed"].append("planning")
        log("planner", f"Plan created with {len(plan.get('search_keywords', []))} keywords")

        # === PHASE 2: DISCOVERY ===
        change_phase(ResearchPhase.DISCOVERY)

        # Build search query: use the research objective directly as primary query
        # ArXiv searches title + abstract, so the full objective gives best relevance
        keywords = plan.get("search_keywords", [])[:8]
        search_query = research_objective

        # Use user-provided categories if available, otherwise use planner's categories
        if not search_categories:
            search_categories = plan.get("search_strategy", {}).get("categories", [])

        date_range = plan.get("search_strategy", {}).get("date_range", "")
        from_date = to_date = None
        if " to " in date_range:
            parts = date_range.split(" to ")
            from_date = parts[0].strip()
            to_date = parts[1].strip()

        # Fetch extra papers (3x) so we have enough after relevance filtering
        fetch_count = max_papers * 3

        log("discovery", f"Searching for papers: '{search_query}' in categories: {search_categories or 'all'}")

        discovery_result = discover_and_process_papers(
            query=search_query,
            max_papers=fetch_count,
            from_date=from_date,
            to_date=to_date,
            categories=search_categories if search_categories else None,
        )

        papers = discovery_result.get("processed_papers", [])

        # Build relevance terms from both objective and planner keywords
        relevance_terms = _extract_relevance_terms(research_objective, keywords)
        log("discovery", f"Relevance terms: {relevance_terms}")

        # Score and filter papers for relevance to the research objective
        scored_papers = []
        for paper in papers:
            score = _compute_relevance_score(paper, relevance_terms)
            scored_papers.append((score, paper))

        scored_papers.sort(key=lambda x: x[0], reverse=True)

        # Keep papers with relevance score > 0, up to max_papers
        relevant_papers = [p for score, p in scored_papers if score > 0][:max_papers]

        # If we got too few relevant papers, fall back to top-scored from ArXiv
        if len(relevant_papers) < max(3, max_papers // 2) and papers:
            relevant_papers = [p for _, p in scored_papers[:max_papers]]
            log("discovery", f"Low relevance matches, using top {len(relevant_papers)} by best available score", level="warning")

        filtered_count = len(papers) - len(relevant_papers)
        if filtered_count > 0:
            log("discovery", f"Filtered out {filtered_count} irrelevant papers")

        papers = relevant_papers
        result["discovered_papers"] = papers
        result["statistics"]["discovery"] = discovery_result.get("statistics", {})
        result["statistics"]["discovery"]["relevance_filtered"] = filtered_count if filtered_count > 0 else 0

        result["phases_completed"].append("discovery")
        log("discovery", f"Discovered {len(papers)} relevant papers", papers_found=len(papers))

        if not papers:
            log("lead_supervisor", "No papers discovered, generating summary report")
            result["final_report"] = _generate_no_results_report(research_objective)
            result["phases_completed"].append("completion")
            return result

        # === PHASE 3: EVALUATION ===
        change_phase(ResearchPhase.EVALUATION)

        evaluation_results = []
        total_score = 0
        eval_stats = {"total": len(papers), "success": 0, "failed": 0}

        for i, paper in enumerate(papers):
            log("evaluation", f"Evaluating paper {i + 1}/{len(papers)}: {paper.get('title', '')[:60]}...")

            eval_result = evaluate_paper(paper)

            if "error" not in eval_result:
                evaluation_results.append(eval_result)
                total_score += eval_result.get("agi_score", 0)
                eval_stats["success"] += 1
                log(
                    "evaluation",
                    f"Paper scored {eval_result['agi_score']}/100 ({eval_result['agi_classification']})",
                )
            else:
                eval_stats["failed"] += 1
                result["errors"].append(eval_result)
                log("evaluation", f"Evaluation failed: {eval_result['error']}", level="error")

        result["evaluation_results"] = evaluation_results
        result["statistics"]["evaluation"] = eval_stats

        avg_score = total_score / len(evaluation_results) if evaluation_results else 0
        result["statistics"]["avg_agi_score"] = round(avg_score, 1)

        result["phases_completed"].append("evaluation")
        log("evaluation", f"Evaluation complete: {eval_stats['success']}/{eval_stats['total']} papers")

        # === PHASE 4: SYNTHESIS ===
        change_phase(ResearchPhase.SYNTHESIS)
        result["final_report"] = _generate_final_report(
            research_objective, papers, evaluation_results, avg_score
        )
        result["phases_completed"].append("synthesis")

        # === COMPLETION ===
        change_phase(ResearchPhase.COMPLETION)
        result["phases_completed"].append("completion")
        result["statistics"]["processing_time"] = round(time.time() - start_time, 1)

        log("lead_supervisor", f"Pipeline completed in {result['statistics']['processing_time']}s")
        return result

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        result["errors"].append({"error": str(e), "phase": "pipeline"})
        result["statistics"]["processing_time"] = round(time.time() - start_time, 1)
        return result


def _extract_relevance_terms(objective: str, keywords: List[str]) -> List[str]:
    """
    Extract meaningful multi-word and single-word terms from the objective and keywords.
    Returns a list of lowercase terms ordered by specificity (multi-word first).
    """
    # Common stop words to exclude
    stop_words = {
        "find", "some", "papers", "on", "about", "the", "a", "an", "and", "or",
        "for", "in", "of", "to", "with", "using", "that", "this", "from", "by",
        "is", "are", "was", "were", "be", "been", "have", "has", "do", "does",
        "how", "what", "which", "where", "when", "who", "research", "study",
        "studies", "paper", "recent", "new", "novel", "based", "related",
    }

    terms = []

    # Add planner keywords as-is (they're already curated phrases)
    for kw in keywords:
        cleaned = kw.strip().lower()
        if cleaned and len(cleaned) > 2:
            terms.append(cleaned)

    # Extract meaningful phrases from objective (2-3 word combinations)
    obj_lower = objective.lower()
    words = re.findall(r'[a-z]+', obj_lower)
    meaningful_words = [w for w in words if w not in stop_words and len(w) > 2]

    # Add bigrams from meaningful words
    for i in range(len(meaningful_words) - 1):
        bigram = f"{meaningful_words[i]} {meaningful_words[i+1]}"
        terms.append(bigram)

    # Add individual meaningful words
    for w in meaningful_words:
        terms.append(w)

    # Deduplicate while preserving order
    seen = set()
    unique_terms = []
    for t in terms:
        if t not in seen:
            seen.add(t)
            unique_terms.append(t)

    return unique_terms


def _compute_relevance_score(paper: Dict[str, Any], terms: List[str]) -> float:
    """
    Compute a relevance score for a paper against the search terms.
    Higher score = more relevant.
    Multi-word term matches are weighted higher than single-word matches.
    """
    title = paper.get("title", "").lower()
    abstract = paper.get("metadata", {}).get("abstract", "").lower()
    text = f"{title} {abstract}"

    score = 0.0
    for term in terms:
        word_count = len(term.split())
        if term in text:
            if term in title:
                # Title matches are worth more
                score += 3.0 * word_count
            else:
                score += 1.5 * word_count

    return score


def _generate_no_results_report(objective: str) -> str:
    return f"""# AGI Research Analysis Report

## Executive Summary

**Research Objective:** {objective}

No papers were discovered for the given research objective.

## Recommendations

1. **Broaden Search Criteria:** Expand search terms and sources
2. **Adjust Date Range:** Consider extending the search timeframe
3. **Review Keywords:** Try alternative or broader keywords

---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""


def _generate_final_report(
    objective: str,
    papers: list,
    evaluations: list,
    avg_score: float,
) -> str:
    sorted_evals = sorted(evaluations, key=lambda x: x.get("agi_score", 0), reverse=True)
    high = [e for e in sorted_evals if e.get("agi_classification") == "high"]
    medium = [e for e in sorted_evals if e.get("agi_classification") == "medium"]
    low = [e for e in sorted_evals if e.get("agi_classification") == "low"]

    report = f"""# AGI Research Analysis Report

## Executive Summary

**Research Objective:** {objective}

**Discovery Overview:**
- Total papers discovered: {len(papers)}
- Papers successfully evaluated: {len(evaluations)}
- Average AGI score: {avg_score:.1f}/100

**AGI Potential Distribution:**
- High AGI Potential: {len(high)} papers
- Medium AGI Potential: {len(medium)} papers
- Low AGI Potential: {len(low)} papers

## Top-Scoring Papers

"""
    for i, ev in enumerate(sorted_evals[:5], 1):
        title = ev.get("paper_title", "Unknown")
        authors = ev.get("paper_authors", [])
        score = ev.get("agi_score", 0)
        classification = ev.get("agi_classification", "unknown")
        innovations = ev.get("key_innovations", [])
        assessment = ev.get("overall_assessment", "")

        report += f"""### {i}. {title}
**Authors:** {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}
**AGI Score:** {score}/100 ({classification})
**Key Innovations:** {', '.join(innovations[:3]) if innovations else 'N/A'}
**Assessment:** {assessment}

"""

    report += f"""---

## Scoring Methodology

### AGI Parameters (Weighted):
1. Novel Problem Solving (15%) | 2. Few-Shot Learning (15%) | 3. Task Transfer (15%)
4. Abstract Reasoning (12%) | 5. Contextual Adaptation (10%) | 6. Multi-Rule Integration (10%)
7. Generalization Efficiency (8%) | 8. Meta-Learning (8%) | 9. World Modeling (4%)
10. Autonomous Goal Setting (3%)

### Score Interpretation:
- 90-100: Exceptional AGI contribution
- 70-89: High AGI potential
- 40-69: Medium AGI potential
- 0-39: Low AGI potential

---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    return report
