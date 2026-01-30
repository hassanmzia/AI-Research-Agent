"""
Celery tasks for async research pipeline execution.
"""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger("research_app.tasks")


@shared_task(bind=True, max_retries=2, soft_time_limit=500, time_limit=600)
def run_research_pipeline(self, session_id: str):
    """
    Execute the full multi-agent research pipeline for a session.
    Runs asynchronously via Celery.
    """
    from research_app.models import ResearchSession, Paper, AGIEvaluation, AgentLog
    from research_app.agents.pipeline import run_pipeline

    try:
        session = ResearchSession.objects.get(id=session_id)
    except ResearchSession.DoesNotExist:
        logger.error(f"Session {session_id} not found")
        return {"error": "Session not found"}

    session.status = ResearchSession.Status.RUNNING
    session.current_phase = ResearchSession.Phase.INITIALIZATION
    session.save()

    def on_phase_change(phase: str):
        phase_map = {
            "planning": ResearchSession.Phase.PLANNING,
            "discovery": ResearchSession.Phase.DISCOVERY,
            "evaluation": ResearchSession.Phase.EVALUATION,
            "synthesis": ResearchSession.Phase.SYNTHESIS,
            "completion": ResearchSession.Phase.COMPLETION,
        }
        session.current_phase = phase_map.get(phase, ResearchSession.Phase.INITIALIZATION)
        session.save(update_fields=["current_phase", "updated_at"])

        # Publish to Redis for WebSocket notifications
        _publish_status_update(session_id, phase)

    def on_log(agent_role: str, message: str, level: str = "info", metadata: dict = None):
        AgentLog.objects.create(
            session=session,
            agent_role=agent_role,
            level=level,
            message=message,
            metadata=metadata or {},
            phase=session.current_phase,
        )

    try:
        result = run_pipeline(
            research_objective=session.research_objective,
            max_papers=session.max_papers,
            days_lookback=session.days_lookback,
            custom_keywords=session.custom_keywords or [],
            search_categories=session.search_categories or [],
            on_phase_change=on_phase_change,
            on_log=on_log,
        )

        # Save discovered papers
        papers_map = {}
        for paper_data in result.get("discovered_papers", []):
            metadata = paper_data.get("metadata", {})
            paper = Paper.objects.create(
                session=session,
                external_id=paper_data.get("id", ""),
                title=paper_data.get("title", ""),
                abstract=metadata.get("abstract", ""),
                authors=metadata.get("authors", []),
                source=metadata.get("source", "arxiv"),
                url=paper_data.get("link", ""),
                doi=metadata.get("doi") or "",
                categories=metadata.get("categories", []),
                published_date=metadata.get("published_date"),
                journal_ref=metadata.get("journal_ref") or "",
                search_query_used=result.get("execution_plan", {}).get("search_keywords", [""])[0] if result.get("execution_plan") else "",
            )
            papers_map[paper_data.get("id", "")] = paper

        # Save evaluations
        for eval_data in result.get("evaluation_results", []):
            paper = papers_map.get(eval_data.get("paper_id"))
            if not paper:
                continue

            param_scores = eval_data.get("parameter_scores", {})
            AGIEvaluation.objects.create(
                paper=paper,
                session=session,
                agi_score=eval_data.get("agi_score", 0),
                classification=eval_data.get("agi_classification", "low"),
                novel_problem_solving=_extract_score(param_scores, "novel_problem_solving"),
                few_shot_learning=_extract_score(param_scores, "few_shot_learning"),
                task_transfer=_extract_score(param_scores, "task_transfer"),
                abstract_reasoning=_extract_score(param_scores, "abstract_reasoning"),
                contextual_adaptation=_extract_score(param_scores, "contextual_adaptation"),
                multi_rule_integration=_extract_score(param_scores, "multi_rule_integration"),
                generalization_efficiency=_extract_score(param_scores, "generalization_efficiency"),
                meta_learning=_extract_score(param_scores, "meta_learning"),
                world_modeling=_extract_score(param_scores, "world_modeling"),
                autonomous_goal_setting=_extract_score(param_scores, "autonomous_goal_setting"),
                parameter_reasoning=_extract_reasoning(param_scores),
                overall_assessment=eval_data.get("overall_assessment", ""),
                key_innovations=eval_data.get("key_innovations", []),
                limitations=eval_data.get("limitations", []),
                confidence_level=eval_data.get("confidence_level", "Medium"),
                score_breakdown=eval_data.get("score_breakdown", {}),
            )

        # Update session
        session.execution_plan = result.get("execution_plan")
        session.final_report = result.get("final_report", "")
        session.synthesis_data = result.get("statistics")
        session.total_papers_discovered = len(result.get("discovered_papers", []))
        session.total_papers_evaluated = len(result.get("evaluation_results", []))
        session.avg_agi_score = result.get("statistics", {}).get("avg_agi_score")
        session.processing_time_seconds = result.get("statistics", {}).get("processing_time")
        session.errors = result.get("errors", [])
        session.mark_completed()

        _publish_status_update(session_id, "completed")

        return {
            "session_id": str(session.id),
            "status": "completed",
            "papers_discovered": session.total_papers_discovered,
            "papers_evaluated": session.total_papers_evaluated,
            "avg_agi_score": session.avg_agi_score,
        }

    except Exception as e:
        logger.error(f"Pipeline failed for session {session_id}: {e}")
        session.mark_failed(str(e))
        _publish_status_update(session_id, "failed")
        raise self.retry(exc=e, countdown=30)


def _extract_score(param_scores: dict, key: str) -> float:
    val = param_scores.get(key, {})
    if isinstance(val, dict):
        return float(val.get("score", 0))
    return float(val) if val else 0


def _extract_reasoning(param_scores: dict) -> dict:
    reasoning = {}
    for key, val in param_scores.items():
        if isinstance(val, dict) and "reasoning" in val:
            reasoning[key] = val["reasoning"]
    return reasoning


def _publish_status_update(session_id: str, phase: str):
    """Publish a status update to Redis for WebSocket consumers."""
    try:
        import redis
        import json
        import os

        r = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
        r.publish(
            "research_updates",
            json.dumps({
                "type": "session_update",
                "session_id": session_id,
                "phase": phase,
                "timestamp": timezone.now().isoformat(),
            }),
        )
    except Exception as e:
        logger.warning(f"Failed to publish status update: {e}")


@shared_task
def run_scheduled_research():
    """Run all due scheduled research jobs."""
    from research_app.models import ScheduledResearch, ResearchSession

    now = timezone.now()
    due_jobs = ScheduledResearch.objects.filter(
        is_active=True,
        next_run_at__lte=now,
    )

    for job in due_jobs:
        session = ResearchSession.objects.create(
            user=job.user,
            title=f"[Scheduled] {job.name}",
            research_objective=job.research_objective,
            max_papers=job.max_papers,
            status=ResearchSession.Status.PENDING,
        )

        task = run_research_pipeline.delay(str(session.id))
        session.celery_task_id = task.id
        session.status = ResearchSession.Status.RUNNING
        session.save()

        job.last_run_at = now
        job.total_runs += 1

        # Calculate next run
        from datetime import timedelta
        freq_map = {
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
            "biweekly": timedelta(weeks=2),
            "monthly": timedelta(days=30),
        }
        job.next_run_at = now + freq_map.get(job.frequency, timedelta(weeks=1))
        job.save()

    return f"Launched {due_jobs.count()} scheduled research jobs"
