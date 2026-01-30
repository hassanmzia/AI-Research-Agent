from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from .mcp_views import mcp_endpoint, a2a_agent_cards, a2a_agent

router = DefaultRouter()
router.register(r'sessions', views.ResearchSessionViewSet, basename='session')
router.register(r'papers', views.PaperViewSet, basename='paper')
router.register(r'evaluations', views.AGIEvaluationViewSet, basename='evaluation')
router.register(r'collections', views.ResearchCollectionViewSet, basename='collection')
router.register(r'scheduled', views.ScheduledResearchViewSet, basename='scheduled')
router.register(r'exports', views.ExportRecordViewSet, basename='export')

urlpatterns = [
    # Auth
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', views.CurrentUserView.as_view(), name='current-user'),

    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Agent logs for a session
    path('sessions/<uuid:session_id>/logs/', views.SessionAgentLogsView.as_view(), name='session-logs'),

    # MCP Protocol
    path('mcp/', mcp_endpoint, name='mcp-endpoint'),

    # A2A Protocol
    path('a2a/agents/', a2a_agent_cards, name='a2a-agent-cards'),
    path('a2a/<str:agent_name>/', a2a_agent, name='a2a-agent'),

    # Router URLs
    path('', include(router.urls)),
]
