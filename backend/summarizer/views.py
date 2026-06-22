from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .extraction import extract_text
from .models import DocumentSummary
from .services import answer_question, summarize_document

ALLOWED_EXTENSIONS = (".pdf", ".docx", ".txt")
MAX_FILE_MB = 50


class SummarizeAPIView(APIView):
    """Upload a legal document and receive a structured AI summary."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded = request.FILES.get("file")
        if uploaded is None:
            return Response(
                {"error": "Please upload a PDF, DOCX or TXT file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        name = (uploaded.name or "").lower()
        if not name.endswith(ALLOWED_EXTENSIONS):
            return Response(
                {"error": "Invalid file format. Please upload PDF or DOCX."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if uploaded.size and uploaded.size > MAX_FILE_MB * 1024 * 1024:
            return Response(
                {"error": "Document too large. Please upload a smaller file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        text = extract_text(uploaded)
        result = summarize_document(text, filename=uploaded.name)

        # Return a bounded slice of the source text so the client can ask
        # follow-up questions without re-uploading.
        result["context"] = text[:8000]
        result["filename"] = uploaded.name

        try:
            DocumentSummary.objects.create(
                user=request.user,
                title=result.get("title", uploaded.name),
                original_filename=uploaded.name,
                summary=result.get("summary", ""),
                metadata={
                    "parties": result.get("parties", []),
                    "effective_date": result.get("effective_date", ""),
                    "termination_date": result.get("termination_date", ""),
                    "provider": result.get("provider", "offline"),
                },
            )
        except Exception:
            pass

        return Response(result)


class DocumentQAAPIView(APIView):
    """Answer a follow-up question about a document's extracted text."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        context = request.data.get("context", "")
        question = request.data.get("question", "")
        if not question:
            return Response(
                {"error": "Please enter a question."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(answer_question(context, question))
