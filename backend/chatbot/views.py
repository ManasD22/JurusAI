from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatMessage, ChatSession
from .services import legal_advice


class LegalAdvisorAPIView(APIView):
    """POST a legal query, get a grounded answer with citations.

    Body: ``{"query": str, "jurisdiction"?: str, "matter_type"?: str,
            "session_id"?: int}``
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = (request.data.get("query") or "").strip()
        if not query:
            return Response(
                {"error": "Please enter a valid query."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = legal_advice(
            query,
            jurisdiction=request.data.get("jurisdiction"),
            matter_type=request.data.get("matter_type"),
        )

        # Persist the turn so it shows up in history (best-effort).
        try:
            session_id = request.data.get("session_id")
            session = None
            if session_id:
                session = ChatSession.objects.filter(id=session_id, user=request.user).first()
            if session is None:
                session = ChatSession.objects.create(
                    user=request.user,
                    title=query[:60],
                )
            ChatMessage.objects.create(session=session, role="user", content=query)
            ChatMessage.objects.create(
                session=session,
                role="assistant",
                content=result["answer"],
                citations=result.get("citations", []),
            )
            result["session_id"] = session.id
        except Exception:
            # History persistence must never break the answer.
            pass

        return Response(result)


class ChatHistoryAPIView(APIView):
    """List the current user's recent conversations for the history panel."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = ChatSession.objects.filter(user=request.user)[:20]
        data = [
            {
                "id": s.id,
                "title": s.title,
                "updated_at": s.updated_at,
                "message_count": s.messages.count(),
            }
            for s in sessions
        ]
        return Response(data)


class ChatSessionDetailAPIView(APIView):
    """Return the full message thread for one conversation."""

    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = ChatSession.objects.filter(id=session_id, user=request.user).first()
        if session is None:
            return Response({"error": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)

        messages = [
            {
                "role": m.role,
                "content": m.content,
                "citations": m.citations,
                "created_at": m.created_at,
            }
            for m in session.messages.all()
        ]
        return Response({"id": session.id, "title": session.title, "messages": messages})
