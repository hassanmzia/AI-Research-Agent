"""
Serializers for the AI Research Multi-Agent System API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from research_app.models import (
    ResearchSession, Paper, AGIEvaluation, AgentLog,
    ResearchCollection, ScheduledResearch, ExportRecord,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class AGIEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AGIEvaluation
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class PaperSerializer(serializers.ModelSerializer):
    evaluation = AGIEvaluationSerializer(read_only=True)

    class Meta:
        model = Paper
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'discovery_timestamp']


class PaperListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for paper lists."""
    agi_score = serializers.FloatField(source='evaluation.agi_score', read_only=True, default=None)
    classification = serializers.CharField(source='evaluation.classification', read_only=True, default=None)

    class Meta:
        model = Paper
        fields = [
            'id', 'title', 'authors', 'source', 'url', 'categories',
            'published_date', 'is_bookmarked', 'agi_score', 'classification',
        ]


class AgentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ResearchSessionSerializer(serializers.ModelSerializer):
    papers_count = serializers.IntegerField(source='papers.count', read_only=True)
    evaluations_count = serializers.IntegerField(source='evaluations.count', read_only=True)

    class Meta:
        model = ResearchSession
        fields = '__all__'
        read_only_fields = [
            'id', 'user', 'status', 'current_phase', 'execution_plan',
            'final_report', 'synthesis_data', 'total_papers_discovered',
            'total_papers_evaluated', 'avg_agi_score', 'processing_time_seconds',
            'errors', 'celery_task_id', 'created_at', 'updated_at', 'completed_at',
        ]


class ResearchSessionCreateSerializer(serializers.Serializer):
    research_objective = serializers.CharField(max_length=2000)
    title = serializers.CharField(max_length=500, required=False, default='')
    max_papers = serializers.IntegerField(min_value=1, max_value=50, default=10)
    days_lookback = serializers.IntegerField(min_value=1, max_value=365, default=14)
    custom_keywords = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    search_categories = serializers.ListField(child=serializers.CharField(), required=False, default=list)


class ResearchSessionDetailSerializer(ResearchSessionSerializer):
    papers = PaperListSerializer(many=True, read_only=True)
    agent_logs = AgentLogSerializer(many=True, read_only=True)

    class Meta(ResearchSessionSerializer.Meta):
        pass


class ResearchCollectionSerializer(serializers.ModelSerializer):
    papers_count = serializers.IntegerField(source='papers.count', read_only=True)

    class Meta:
        model = ResearchCollection
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ResearchCollectionDetailSerializer(ResearchCollectionSerializer):
    papers = PaperListSerializer(many=True, read_only=True)

    class Meta(ResearchCollectionSerializer.Meta):
        pass


class ScheduledResearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledResearch
        fields = '__all__'
        read_only_fields = ['id', 'user', 'last_run_at', 'next_run_at', 'total_runs', 'created_at']


class ExportRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportRecord
        fields = '__all__'
        read_only_fields = ['id', 'user', 'file_content', 'created_at']


class ExportRequestSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=ExportRecord.Format.choices)


class DashboardStatsSerializer(serializers.Serializer):
    total_sessions = serializers.IntegerField()
    total_papers = serializers.IntegerField()
    total_evaluations = serializers.IntegerField()
    avg_agi_score = serializers.FloatField()
    high_agi_count = serializers.IntegerField()
    medium_agi_count = serializers.IntegerField()
    low_agi_count = serializers.IntegerField()
    recent_sessions = ResearchSessionSerializer(many=True)
    top_papers = PaperListSerializer(many=True)
    score_distribution = serializers.ListField()
    papers_by_source = serializers.ListField()
    sessions_over_time = serializers.ListField()
