"""
Configuration for the multi-agent research system.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentConfig:
    """System configuration management."""
    max_papers_per_run: int = 10
    research_days_lookback: int = 14
    log_level: str = "INFO"
    max_retries: int = 3
    request_timeout: int = 120
    retry_delay: int = 5
    openai_model_name: str = "gpt-4o-mini"

    @classmethod
    def from_env(cls) -> "AgentConfig":
        return cls(
            max_papers_per_run=int(os.getenv("MAX_PAPERS_PER_RUN", "10")),
            research_days_lookback=int(os.getenv("RESEARCH_DAYS_LOOKBACK", "14")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "120")),
            retry_delay=int(os.getenv("RETRY_DELAY", "5")),
            openai_model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
        )


_config: Optional[AgentConfig] = None


def get_config() -> AgentConfig:
    global _config
    if _config is None:
        _config = AgentConfig.from_env()
    return _config


# AGI Parameters with weights (must sum to 1.0)
AGI_PARAMETERS = {
    "novel_problem_solving": {
        "weight": 0.15,
        "description": "Ability to solve new problems that weren't in training data",
    },
    "few_shot_learning": {
        "weight": 0.15,
        "description": "Learning new tasks from minimal examples",
    },
    "task_transfer": {
        "weight": 0.15,
        "description": "Applying learned skills to different domains",
    },
    "abstract_reasoning": {
        "weight": 0.12,
        "description": "Logical thinking and pattern recognition",
    },
    "contextual_adaptation": {
        "weight": 0.10,
        "description": "Adapting behavior based on context",
    },
    "multi_rule_integration": {
        "weight": 0.10,
        "description": "Following multiple complex rules simultaneously",
    },
    "generalization_efficiency": {
        "weight": 0.08,
        "description": "Generalizing from small amounts of data",
    },
    "meta_learning": {
        "weight": 0.08,
        "description": "Learning how to learn new tasks",
    },
    "world_modeling": {
        "weight": 0.04,
        "description": "Understanding and modeling complex environments",
    },
    "autonomous_goal_setting": {
        "weight": 0.03,
        "description": "Setting and pursuing own objectives",
    },
}
