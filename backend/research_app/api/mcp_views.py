"""
MCP and A2A protocol API endpoints.
"""
import json
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mcp_endpoint(request):
    """
    MCP (Model Context Protocol) JSON-RPC endpoint.

    Supports:
      - initialize: Get server capabilities
      - tools/list: List available tools
      - tools/call: Execute a tool
    """
    from research_app.mcp.server import handle_mcp_request

    try:
        result = handle_mcp_request(request.data)
        return Response(result)
    except Exception as e:
        return Response(
            {"jsonrpc": "2.0", "error": {"code": -32000, "message": str(e)}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def a2a_agent_cards(request):
    """Return all available A2A agent cards."""
    from research_app.a2a.protocol import get_agent_cards
    return Response(get_agent_cards())


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def a2a_agent(request, agent_name):
    """
    A2A protocol endpoint for a specific agent.

    GET: Returns the agent's card
    POST: Sends a task to the agent

    Body for POST:
    {
        "method": "tasks/send" | "tasks/get" | "tasks/cancel",
        "data": { ... }
    }
    """
    from research_app.a2a.protocol import handle_a2a_request

    if request.method == 'GET':
        result = handle_a2a_request(agent_name, "agent_card", {})
    else:
        method = request.data.get("method", "tasks/send")
        data = request.data.get("data", request.data)
        result = handle_a2a_request(agent_name, method, data)

    return Response(result)
