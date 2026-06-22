from django.urls import path

from .views import (
    DraftDetailAPIView,
    ExportPDFAPIView,
    GenerateDocumentAPIView,
    RecentDraftsAPIView,
    TemplatesAPIView,
)

urlpatterns = [
    path("templates/", TemplatesAPIView.as_view()),
    path("generate/", GenerateDocumentAPIView.as_view()),
    path("drafts/", RecentDraftsAPIView.as_view()),
    path("drafts/<int:draft_id>/", DraftDetailAPIView.as_view()),
    path("export/", ExportPDFAPIView.as_view()),
]
