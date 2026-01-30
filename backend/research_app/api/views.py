"""
Views for the AI Research Multi-Agent System API.
"""
import json
import csv
import io
from django.db.models import Avg, Count, Q, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from research_app.models import (
    ResearchSession, Paper, AGIEvaluation, AgentLog,
    ResearchCollection, ScheduledResearch, ExportRecord,
)
from .serializers import (
    UserSerializer, RegisterSerializer,
    ResearchSessionSerializer, ResearchSessionCreateSerializer,
    ResearchSessionDetailSerializer,
    PaperSerializer, PaperListSerializer,
    AGIEvaluationSerializer,
    AgentLogSerializer,
    ResearchCollectionSerializer,
    ScheduledResearchSerializer,
    ExportRecordSerializer, ExportRequestSerializer,
    DashboardStatsSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class CurrentUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ResearchSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ResearchSessionSerializer

    def get_queryset(self):
        return ResearchSession.objects.filter(user=self.request.user).select_related('user')

    def get_serializer_class(self):
        if self.action == 'create':
            return ResearchSessionCreateSerializer
        if self.action == 'retrieve':
            return ResearchSessionDetailSerializer
        return ResearchSessionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = ResearchSession.objects.create(
            user=request.user,
            research_objective=serializer.validated_data['research_objective'],
            title=serializer.validated_data.get('title', ''),
            max_papers=serializer.validated_data.get('max_papers', 10),
            days_lookback=serializer.validated_data.get('days_lookback', 14),
            custom_keywords=serializer.validated_data.get('custom_keywords', []),
            search_categories=serializer.validated_data.get('search_categories', []),
            status=ResearchSession.Status.PENDING,
        )

        # Launch async research task
        from research_app.tasks import run_research_pipeline
        task = run_research_pipeline.delay(str(session.id))
        session.celery_task_id = task.id
        session.status = ResearchSession.Status.RUNNING
        session.save()

        return Response(
            ResearchSessionSerializer(session).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        session = self.get_object()
        if session.status == ResearchSession.Status.RUNNING:
            from config.celery_app import app
            if session.celery_task_id:
                app.control.revoke(session.celery_task_id, terminate=True)
            session.status = ResearchSession.Status.CANCELLED
            session.save()
            return Response({'status': 'cancelled'})
        return Response({'error': 'Session is not running'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        session = self.get_object()
        serializer = ExportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        export_format = serializer.validated_data['format']

        content = self._generate_export(session, export_format)
        file_name = f"research_report_{session.id}.{export_format}"

        export_record = ExportRecord.objects.create(
            session=session,
            user=request.user,
            format=export_format,
            file_name=file_name,
            file_content=content,
        )
        return Response(ExportRecordSerializer(export_record).data)

    def _generate_export(self, session, export_format):
        if export_format == 'json':
            data = {
                'session': ResearchSessionDetailSerializer(session).data,
                'papers': PaperSerializer(session.papers.all(), many=True).data,
                'evaluations': AGIEvaluationSerializer(
                    AGIEvaluation.objects.filter(session=session), many=True
                ).data,
            }
            return json.dumps(data, indent=2, default=str)
        elif export_format == 'markdown':
            return session.final_report or 'No report generated.'
        elif export_format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Title', 'Authors', 'Source', 'AGI Score', 'Classification', 'URL'])
            for paper in session.papers.select_related('evaluation').all():
                eval_obj = getattr(paper, 'evaluation', None)
                writer.writerow([
                    paper.title,
                    '; '.join([a.get('name', '') if isinstance(a, dict) else a for a in paper.authors]),
                    paper.source,
                    eval_obj.agi_score if eval_obj else '',
                    eval_obj.get_classification_display() if eval_obj else '',
                    paper.url,
                ])
            return output.getvalue()
        return session.final_report or ''


class PaperViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaperSerializer
    filterset_fields = ['source', 'is_bookmarked', 'session']
    search_fields = ['title', 'abstract']
    ordering_fields = ['published_date', 'created_at', 'title']

    def get_queryset(self):
        return Paper.objects.filter(
            session__user=self.request.user
        ).select_related('evaluation')

    def get_serializer_class(self):
        if self.action == 'list':
            return PaperListSerializer
        return PaperSerializer

    @action(detail=True, methods=['post'])
    def bookmark(self, request, pk=None):
        paper = self.get_object()
        paper.is_bookmarked = not paper.is_bookmarked
        paper.save()
        return Response({'is_bookmarked': paper.is_bookmarked})

    @action(detail=True, methods=['patch'])
    def notes(self, request, pk=None):
        paper = self.get_object()
        paper.user_notes = request.data.get('notes', '')
        paper.save()
        return Response({'user_notes': paper.user_notes})


class AGIEvaluationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AGIEvaluationSerializer
    filterset_fields = ['classification', 'session']
    ordering_fields = ['agi_score', 'created_at']

    def get_queryset(self):
        return AGIEvaluation.objects.filter(
            session__user=self.request.user
        ).select_related('paper')


class SessionAgentLogsView(generics.ListAPIView):
    serializer_class = AgentLogSerializer

    def get_queryset(self):
        session_id = self.kwargs['session_id']
        return AgentLog.objects.filter(
            session_id=session_id,
            session__user=self.request.user,
        )


class ResearchCollectionViewSet(viewsets.ModelViewSet):
    serializer_class = ResearchCollectionSerializer

    def get_queryset(self):
        return ResearchCollection.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_paper(self, request, pk=None):
        collection = self.get_object()
        paper_id = request.data.get('paper_id')
        try:
            paper = Paper.objects.get(id=paper_id, session__user=request.user)
            collection.papers.add(paper)
            return Response({'status': 'added'})
        except Paper.DoesNotExist:
            return Response({'error': 'Paper not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_paper(self, request, pk=None):
        collection = self.get_object()
        paper_id = request.data.get('paper_id')
        collection.papers.remove(paper_id)
        return Response({'status': 'removed'})


class ScheduledResearchViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduledResearchSerializer

    def get_queryset(self):
        return ScheduledResearch.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        scheduled = self.get_object()
        scheduled.is_active = not scheduled.is_active
        scheduled.save()
        return Response({'is_active': scheduled.is_active})


class ExportRecordViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ExportRecordSerializer

    def get_queryset(self):
        return ExportRecord.objects.filter(user=self.request.user)


class DashboardView(generics.GenericAPIView):
    """Dashboard analytics endpoint."""

    def get(self, request):
        user = request.user
        sessions = ResearchSession.objects.filter(user=user)
        evaluations = AGIEvaluation.objects.filter(session__user=user)

        # Aggregate stats
        total_sessions = sessions.count()
        total_papers = Paper.objects.filter(session__user=user).count()
        total_evaluations = evaluations.count()

        agg = evaluations.aggregate(avg_score=Avg('agi_score'))
        avg_agi_score = round(agg['avg_score'] or 0, 1)

        high_count = evaluations.filter(classification='high').count()
        medium_count = evaluations.filter(classification='medium').count()
        low_count = evaluations.filter(classification='low').count()

        # Recent sessions
        recent_sessions = sessions[:5]

        # Top papers
        top_papers = Paper.objects.filter(
            session__user=user,
            evaluation__isnull=False,
        ).select_related('evaluation').order_by('-evaluation__agi_score')[:10]

        # Score distribution (buckets of 10)
        score_distribution = []
        for lower in range(0, 100, 10):
            upper = lower + 10
            count = evaluations.filter(agi_score__gte=lower, agi_score__lt=upper).count()
            score_distribution.append({'range': f'{lower}-{upper}', 'count': count})

        # Papers by source
        papers_by_source = list(
            Paper.objects.filter(session__user=user)
            .values('source')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Sessions over time (last 30 days)
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        sessions_over_time = list(
            sessions.filter(created_at__gte=thirty_days_ago)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        data = {
            'total_sessions': total_sessions,
            'total_papers': total_papers,
            'total_evaluations': total_evaluations,
            'avg_agi_score': avg_agi_score,
            'high_agi_count': high_count,
            'medium_agi_count': medium_count,
            'low_agi_count': low_count,
            'recent_sessions': ResearchSessionSerializer(recent_sessions, many=True).data,
            'top_papers': PaperListSerializer(top_papers, many=True).data,
            'score_distribution': score_distribution,
            'papers_by_source': papers_by_source,
            'sessions_over_time': [
                {'date': str(s['date']), 'count': s['count']} for s in sessions_over_time
            ],
        }

        return Response(data)
