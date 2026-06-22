from django.urls import path

from .views import (
    ChatHistoryAPIView,
    ChatSessionDetailAPIView,
    LegalAdvisorAPIView,
)

urlpatterns = [
    path("advice/", LegalAdvisorAPIView.as_view()),
    path("history/", ChatHistoryAPIView.as_view()),
    path("history/<int:session_id>/", ChatSessionDetailAPIView.as_view()),
]
