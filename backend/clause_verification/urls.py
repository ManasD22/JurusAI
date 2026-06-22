from django.urls import path

from .views import (
    AnalyzeUploadAPIView,
    DetectDocumentAPIView,
    VerifyDocumentAPIView,
)

urlpatterns = [
    # New single-call flow used by the frontend.
    path("analyze/", AnalyzeUploadAPIView.as_view()),
    # Legacy by-id flows (kept for backward compatibility).
    path("detect/<int:document_id>/", DetectDocumentAPIView.as_view()),
    path("verify/<int:document_id>/", VerifyDocumentAPIView.as_view()),
]
