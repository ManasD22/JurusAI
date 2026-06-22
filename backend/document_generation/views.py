import io

from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GeneratedDocument
from .services import generate_document
from .templates_catalog import (
    CATEGORIES,
    DEPARTMENTS,
    SUPPORTED_LANGUAGES,
    TEMPLATES,
)


class TemplatesAPIView(APIView):
    """Return the template catalog used by the Generate Document + Admin pages."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "templates": TEMPLATES,
                "categories": CATEGORIES,
                "departments": DEPARTMENTS,
                "languages": SUPPORTED_LANGUAGES,
            }
        )


class GenerateDocumentAPIView(APIView):
    """Generate a legal document from a template or a free-form request."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        doc_type = request.data.get("type") or request.data.get("template_id") or ""
        details = request.data.get("details") or {}
        language = request.data.get("language") or "English"
        custom_request = request.data.get("custom_request") or request.data.get("prompt") or ""

        if not doc_type and not custom_request:
            return Response(
                {"error": "Please fill all required details before generating the document."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if isinstance(details, str):
            # Allow details to arrive as a JSON string.
            import json

            try:
                details = json.loads(details)
            except Exception:
                details = {"notes": details}

        result = generate_document(
            doc_type=doc_type,
            details=details,
            language=language,
            custom_request=custom_request,
        )

        try:
            doc = GeneratedDocument.objects.create(
                user=request.user,
                title=result["title"],
                doc_type=result["doc_type"],
                language=result["language"],
                content=result["document"],
                status="completed",
            )
            result["id"] = doc.id
        except Exception:
            pass

        return Response(result)


class RecentDraftsAPIView(APIView):
    """List the current user's recent drafts for the 'Recent Drafts' panel."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        drafts = GeneratedDocument.objects.filter(user=request.user)[:15]
        return Response(
            [
                {
                    "id": d.id,
                    "title": d.title,
                    "doc_type": d.doc_type,
                    "language": d.language,
                    "status": d.status,
                    "updated_at": d.updated_at,
                }
                for d in drafts
            ]
        )


class DraftDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, draft_id):
        draft = GeneratedDocument.objects.filter(id=draft_id, user=request.user).first()
        if draft is None:
            return Response({"error": "Draft not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {
                "id": draft.id,
                "title": draft.title,
                "doc_type": draft.doc_type,
                "language": draft.language,
                "content": draft.content,
                "status": draft.status,
            }
        )


class ExportPDFAPIView(APIView):
    """Render arbitrary title + content into a downloadable PDF.

    Reused by Document Summary ('Download as PDF') and Clause Verification
    ('Download Corrected'). Falls back to a .txt download if reportlab is
    not installed.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = (request.data.get("title") or "JurisAI Document").strip()
        content = request.data.get("content") or ""

        pdf_bytes = _render_pdf(title, content)
        if pdf_bytes is not None:
            response = HttpResponse(pdf_bytes, content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{_safe_name(title)}.pdf"'
            return response

        # Fallback: plain text download.
        response = HttpResponse(f"{title}\n\n{content}", content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="{_safe_name(title)}.txt"'
        return response


def _safe_name(title: str) -> str:
    import re

    return re.sub(r"[^A-Za-z0-9_-]+", "_", title)[:60] or "document"


def _render_pdf(title: str, content: str):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except Exception:
        return None

    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        styles = getSampleStyleSheet()
        story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
        for block in content.split("\n"):
            block = block.strip()
            if block:
                story.append(Paragraph(block.replace("&", "&amp;").replace("<", "&lt;"), styles["BodyText"]))
            else:
                story.append(Spacer(1, 8))
        doc.build(story)
        return buffer.getvalue()
    except Exception:
        return None
