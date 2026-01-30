from django.contrib import admin
from .models import (
    ResearchSession, Paper, AGIEvaluation, AgentLog,
    ResearchCollection, ScheduledResearch, ExportRecord,
)


@admin.register(ResearchSession)
class ResearchSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'current_phase', 'total_papers_discovered', 'avg_agi_score', 'created_at']
    list_filter = ['status', 'current_phase', 'created_at']
    search_fields = ['research_objective', 'title']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at']


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ['title', 'source', 'published_date', 'is_bookmarked', 'created_at']
    list_filter = ['source', 'is_bookmarked']
    search_fields = ['title', 'abstract']


@admin.register(AGIEvaluation)
class AGIEvaluationAdmin(admin.ModelAdmin):
    list_display = ['paper', 'agi_score', 'classification', 'confidence_level', 'created_at']
    list_filter = ['classification', 'confidence_level']
    ordering = ['-agi_score']


@admin.register(AgentLog)
class AgentLogAdmin(admin.ModelAdmin):
    list_display = ['agent_role', 'level', 'message', 'phase', 'created_at']
    list_filter = ['agent_role', 'level', 'phase']


@admin.register(ResearchCollection)
class ResearchCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_public', 'created_at']
    list_filter = ['is_public']


@admin.register(ScheduledResearch)
class ScheduledResearchAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'frequency', 'is_active', 'last_run_at', 'next_run_at']
    list_filter = ['frequency', 'is_active']


@admin.register(ExportRecord)
class ExportRecordAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'format', 'user', 'created_at']
    list_filter = ['format']
