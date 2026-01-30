"""
Evaluation Agent - Evaluates papers using the 10-parameter AGI framework.
"""
import json
import logging
from typing import Dict, List, Any, Tuple

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import APIError, RateLimitError, APITimeoutError

from .config import get_config, AGI_PARAMETERS

logger = logging.getLogger("research_app.agents.evaluation")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type((APIError, RateLimitError, APITimeoutError)),
)
def call_llm_with_retry(llm, messages):
    try:
        return llm.invoke(messages)
    except RateLimitError:
        logger.warning("Rate limit hit, backing off")
        raise
    except APITimeoutError:
        logger.warning("API timeout, retrying")
        raise


def get_agi_metrics_prompt(title: str, abstract: str, authors: List[str]) -> str:
    authors_str = ", ".join(authors[:5])
    return f"""EVALUATE THIS RESEARCH PAPER FOR AGI (ARTIFICIAL GENERAL INTELLIGENCE) POTENTIAL

## PAPER DETAILS
**Title:** {title}
**Authors:** {authors_str}
**Abstract:** {abstract}

## EVALUATION TASK
Rate this paper on each AGI parameter below using a 1-10 scale where:
- **1-3:** No/minimal AGI relevance
- **4-6:** Some AGI potential but limited
- **7-8:** Strong AGI contribution
- **9-10:** Exceptional AGI breakthrough

## AGI PARAMETERS TO EVALUATE

1. **Novel Problem Solving (15% weight)**
2. **Few-Shot Learning (15% weight)**
3. **Task Transfer (15% weight)**
4. **Abstract Reasoning (12% weight)**
5. **Contextual Adaptation (10% weight)**
6. **Multi-Rule Integration (10% weight)**
7. **Generalization Efficiency (8% weight)**
8. **Meta-Learning (8% weight)**
9. **World Modeling (4% weight)**
10. **Autonomous Goal Setting (3% weight)**

## OUTPUT FORMAT
Provide your evaluation as a JSON object:

```json
{{
    "parameter_scores": {{
        "novel_problem_solving": {{"score": X, "reasoning": "explanation"}},
        "few_shot_learning": {{"score": X, "reasoning": "explanation"}},
        "task_transfer": {{"score": X, "reasoning": "explanation"}},
        "abstract_reasoning": {{"score": X, "reasoning": "explanation"}},
        "contextual_adaptation": {{"score": X, "reasoning": "explanation"}},
        "multi_rule_integration": {{"score": X, "reasoning": "explanation"}},
        "generalization_efficiency": {{"score": X, "reasoning": "explanation"}},
        "meta_learning": {{"score": X, "reasoning": "explanation"}},
        "world_modeling": {{"score": X, "reasoning": "explanation"}},
        "autonomous_goal_setting": {{"score": X, "reasoning": "explanation"}}
    }},
    "overall_agi_assessment": "2-3 sentence summary",
    "key_innovations": ["innovation1", "innovation2", "innovation3"],
    "limitations": ["limitation1", "limitation2"],
    "confidence_level": "High/Medium/Low"
}}
```

Be conservative: Reserve high scores (7+) for truly exceptional AGI contributions.
Evaluate the paper now:"""


def calculate_agi_score(parameter_scores: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
    """Calculate weighted AGI score from individual parameter scores."""
    total_weighted = 0.0
    total_weight = 0.0
    contributions = {}

    for name, config in AGI_PARAMETERS.items():
        if name in parameter_scores:
            score = parameter_scores[name]
            weight = config["weight"]
            contribution = score * weight
            total_weighted += contribution
            total_weight += weight
            contributions[name] = {
                "score": score,
                "weight": weight,
                "contribution": round(contribution, 1),
            }

    final_score = (total_weighted / total_weight) * 10 if total_weight > 0 else 0.0

    if final_score >= 70:
        classification = "high"
    elif final_score >= 40:
        classification = "medium"
    else:
        classification = "low"

    breakdown = {
        "final_score": round(final_score, 1),
        "classification": classification,
        "parameter_contributions": contributions,
        "total_weight_used": total_weight,
    }

    return round(final_score, 1), breakdown


def evaluate_paper(paper: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate a single paper using the AGI framework."""
    config = get_config()
    llm = ChatOpenAI(model_name=config.openai_model_name, temperature=0.2)

    title = paper.get("title", "Unknown")
    metadata = paper.get("metadata", {})
    abstract = metadata.get("abstract", "")
    authors = []
    for a in metadata.get("authors", []):
        if isinstance(a, dict):
            authors.append(a.get("name", "Unknown"))
        elif isinstance(a, str):
            authors.append(a)

    if not abstract or len(abstract) < 50:
        return {"error": "Insufficient abstract content", "paper_id": paper.get("id")}

    prompt = get_agi_metrics_prompt(title, abstract, authors)

    system_msg = SystemMessage(
        content="You are an expert AGI evaluator. Analyze research papers for their contribution "
        "to Artificial General Intelligence advancement. Provide precise, evidence-based "
        "evaluations in the requested JSON format."
    )

    try:
        response = call_llm_with_retry(llm, [system_msg, HumanMessage(content=prompt)])
        eval_text = response.content

        json_start = eval_text.find("{")
        json_end = eval_text.rfind("}") + 1
        if json_start < 0 or json_end <= json_start:
            return {"error": "No valid JSON in LLM response", "paper_id": paper.get("id")}

        eval_data = json.loads(eval_text[json_start:json_end])

        param_scores = {}
        if "parameter_scores" in eval_data:
            for param, details in eval_data["parameter_scores"].items():
                if isinstance(details, dict) and "score" in details:
                    param_scores[param] = details["score"]

        weighted_score, breakdown = calculate_agi_score(param_scores)

        return {
            "paper_id": paper.get("id", ""),
            "paper_title": title,
            "paper_authors": authors,
            "paper_source": metadata.get("source", "unknown"),
            "paper_url": paper.get("link", ""),
            "agi_score": weighted_score,
            "agi_classification": breakdown["classification"],
            "parameter_scores": eval_data.get("parameter_scores", {}),
            "overall_assessment": eval_data.get("overall_agi_assessment", ""),
            "key_innovations": eval_data.get("key_innovations", []),
            "limitations": eval_data.get("limitations", []),
            "confidence_level": eval_data.get("confidence_level", "Medium"),
            "score_breakdown": breakdown,
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error for paper {paper.get('id')}: {e}")
        return {"error": f"JSON parse error: {e}", "paper_id": paper.get("id")}
    except Exception as e:
        logger.error(f"Evaluation error for paper {paper.get('id')}: {e}")
        return {"error": str(e), "paper_id": paper.get("id")}
