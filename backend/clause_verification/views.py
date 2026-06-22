from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from summarizer.extraction import extract_text

from .services import analyze_document, analyze_text_for_ui

ALLOWED_EXTENSIONS = (".pdf", ".docx", ".txt")


class AnalyzeUploadAPIView(APIView):
    """Single-call clause verification: upload a contract, get the full report.

    This powers the React "Clause Verification" screen (risk score, clause
    count, flagged loopholes + corrected versions).
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded = request.FILES.get("file")
        if uploaded is None:
            return Response(
                {"error": "Please upload a contract (PDF, DOCX or TXT)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        name = (uploaded.name or "").lower()
        if not name.endswith(ALLOWED_EXTENSIONS):
            return Response(
                {"error": "Invalid file format. Please upload PDF, DOCX or TXT."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        text = extract_text(uploaded)
        if not text or not text.strip():
            return Response(
                {"error": "No valid clauses found in the document."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = analyze_text_for_ui(text, document_title=uploaded.name)
        result["extracted_text"] = text[:8000]
        return Response(result)


class DetectDocumentAPIView(APIView):
    """Legacy: analyze a previously uploaded document by id."""

    permission_classes = [IsAuthenticated]

    def get(self, request, document_id):
        result = analyze_document(document_id, request.user)
        return Response(result)


class VerifyDocumentAPIView(APIView):
    """Legacy alias for the by-id verification flow."""

    permission_classes = [IsAuthenticated]

    def get(self, request, document_id):
        result = analyze_document(document_id, request.user)
        return Response(result)
