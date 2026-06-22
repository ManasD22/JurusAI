from django.urls import path

from .views import DocumentQAAPIView, SummarizeAPIView

urlpatterns = [
    path("summarize/", SummarizeAPIView.as_view()),
    path("ask/", DocumentQAAPIView.as_view()),
]
