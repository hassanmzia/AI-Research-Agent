"""
Models for the AI Research Multi-Agent System.
Covers research sessions, papers, evaluations, agent activity, and user management.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ResearchSession(models.Model):
    """A research session represents one complete run of the multi-agent pipeline."""

    class Phase(models.TextChoices):
        INITIALIZATION = 'initialization', 'Initialization'
        PLANNING = 'planning', 'Planning'
        DISCOVERY = 'discovery', 'Discovery'
        EVALUATION = 'evaluation', 'Evaluation'
        SYNTHESIS = 'synthesis', 'Synthesis'
        COMPLETION = 'completion', 'Completion'
        FAILED = 'failed', 'Failed'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='research_sessions')
    title = models.CharField(max_length=500, blank=True)
    research_objective = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    current_phase = models.CharField(max_length=20, choices=Phase.choices, default=Phase.INITIALIZATION)

    # Configuration
    max_papers = models.IntegerField(default=10)
    days_lookback = models.IntegerField(default=14)
    custom_keywords = models.JSONField(default=list, blank=True)
    search_categories = models.JSONField(default=list, blank=True)

    # Results
    execution_plan = models.JSONField(null=True, blank=True)
    final_report = models.TextField(blank=True)
    synthesis_data = models.JSONField(null=True, blank=True)

    # Stats
    total_papers_discovered = models.IntegerField(default=0)
    total_papers_evaluated = models.IntegerField(default=0)
    avg_agi_score = models.FloatField(null=True, blank=True)
    processing_time_seconds = models.FloatField(null=True, blank=True)

    # Errors
    errors = models.JSONField(default=list, blank=True)

    # Task tracking
    celery_task_id = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"[{self.status}] {self.research_objective[:80]}"

    def mark_completed(self):
        self.status = self.Status.COMPLETED
        self.current_phase = self.Phase.COMPLETION
        self.completed_at = timezone.now()
        self.save()

    def mark_failed(self, error_message: str):
        self.status = self.Status.FAILED
        self.current_phase = self.Phase.FAILED
        self.errors.append({
            'message': error_message,
            'timestamp': timezone.now().isoformat(),
        })
        self.completed_at = timezone.now()
        self.save()


class Paper(models.Model):
    """A discovered research paper."""

    class Source(models.TextChoices):
        ARXIV = 'arxiv', 'arXiv'
        IEEE = 'ieee', 'IEEE'
        ACL = 'acl', 'ACL'
        SEMANTIC_SCHOLAR = 'semantic_scholar', 'Semantic Scholar'
        MANUAL = 'manual', 'Manual Entry'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ResearchSession, on_delete=models.CASCADE, related_name='papers')
    external_id = models.CharField(max_length=255, blank=True)
    title = models.TextField()
    abstract = models.TextField()
    authors = models.JSONField(default=list)
    source = models.CharField(max_length=30, choices=Source.choices, default=Source.ARXIV)
    url = models.URLField(max_length=500, blank=True)
    doi = models.CharField(max_length=255, blank=True)
    categories = models.JSONField(default=list)
    published_date = models.DateTimeField(null=True, blank=True)
    journal_ref = models.CharField(max_length=500, blank=True)
    pdf_url = models.URLField(max_length=500, blank=True)

    # Discovery metadata
    search_query_used = models.TextField(blank=True)
    discovery_timestamp = models.DateTimeField(auto_now_add=True)

    # Bookmarking
    is_bookmarked = models.BooleanField(default=False)
    user_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['session', '-published_date']),
            models.Index(fields=['external_id']),
            models.Index(fields=['source']),
        ]

    def __str__(self):
        return self.title[:100]


class AGIEvaluation(models.Model):
    """AGI evaluation result for a paper using the 10-parameter framework."""

    class Classification(models.TextChoices):
        HIGH = 'high', 'High AGI Potential'
        MEDIUM = 'medium', 'Medium AGI Potential'
        LOW = 'low', 'Low AGI Potential'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paper = models.OneToOneField(Paper, on_delete=models.CASCADE, related_name='evaluation')
    session = models.ForeignKey(ResearchSession, on_delete=models.CASCADE, related_name='evaluations')

    # Weighted AGI Score (0-100)
    agi_score = models.FloatField()
    classification = models.CharField(max_length=10, choices=Classification.choices)

    # 10 AGI Parameter Scores (each 1-10)
    novel_problem_solving = models.FloatField(default=0)
    few_shot_learning = models.FloatField(default=0)
    task_transfer = models.FloatField(default=0)
    abstract_reasoning = models.FloatField(default=0)
    contextual_adaptation = models.FloatField(default=0)
    multi_rule_integration = models.FloatField(default=0)
    generalization_efficiency = models.FloatField(default=0)
    meta_learning = models.FloatField(default=0)
    world_modeling = models.FloatField(default=0)
    autonomous_goal_setting = models.FloatField(default=0)

    # Detailed reasoning per parameter
    parameter_reasoning = models.JSONField(default=dict)

    # Summary fields
    overall_assessment = models.TextField(blank=True)
    key_innovations = models.JSONField(default=list)
    limitations = models.JSONField(default=list)
    confidence_level = models.CharField(max_length=20, default='Medium')

    # Score breakdown
    score_breakdown = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-agi_score']
        indexes = [
            models.Index(fields=['-agi_score']),
            models.Index(fields=['classification']),
            models.Index(fields=['session', '-agi_score']),
        ]

    def __str__(self):
        return f"{self.paper.title[:60]} - Score: {self.agi_score}"


class AgentLog(models.Model):
    """Tracks activity of each agent in the multi-agent system."""

    class AgentRole(models.TextChoices):
        LEAD_SUPERVISOR = 'lead_supervisor', 'Lead Supervisor'
        PLANNER = 'planner', 'Planner'
        DISCOVERY_SUPERVISOR = 'discovery', 'Discovery Supervisor'
        EVALUATION_SUPERVISOR = 'evaluation', 'Evaluation Supervisor'
        MCP_TOOL = 'mcp_tool', 'MCP Tool Server'
        A2A_AGENT = 'a2a_agent', 'A2A Agent'

    class LogLevel(models.TextChoices):
        INFO = 'info', 'Info'
        WARNING = 'warning', 'Warning'
        ERROR = 'error', 'Error'
        DEBUG = 'debug', 'Debug'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ResearchSession, on_delete=models.CASCADE, related_name='agent_logs')
    agent_role = models.CharField(max_length=30, choices=AgentRole.choices)
    level = models.CharField(max_length=10, choices=LogLevel.choices, default=LogLevel.INFO)
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    phase = models.CharField(max_length=20, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['agent_role']),
        ]

    def __str__(self):
        return f"[{self.agent_role}] {self.message[:80]}"


class ResearchCollection(models.Model):
    """User-curated collection of papers across sessions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    papers = models.ManyToManyField(Paper, related_name='collections', blank=True)
    is_public = models.BooleanField(default=False)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


class ScheduledResearch(models.Model):
    """Recurring research jobs that run on a schedule."""

    class Frequency(models.TextChoices):
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        BIWEEKLY = 'biweekly', 'Bi-Weekly'
        MONTHLY = 'monthly', 'Monthly'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_research')
    name = models.CharField(max_length=255)
    research_objective = models.TextField()
    frequency = models.CharField(max_length=20, choices=Frequency.choices, default=Frequency.WEEKLY)
    max_papers = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    total_runs = models.IntegerField(default=0)
    notify_on_completion = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.frequency})"


class ExportRecord(models.Model):
    """Tracks exported reports and data."""

    class Format(models.TextChoices):
        PDF = 'pdf', 'PDF'
        MARKDOWN = 'markdown', 'Markdown'
        JSON = 'json', 'JSON'
        CSV = 'csv', 'CSV'
        EXCEL = 'excel', 'Excel'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ResearchSession, on_delete=models.CASCADE, related_name='exports')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exports')
    format = models.CharField(max_length=10, choices=Format.choices)
    file_name = models.CharField(max_length=500)
    file_content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.file_name} ({self.format})"
