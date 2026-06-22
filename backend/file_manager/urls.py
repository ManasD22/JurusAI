from django.urls import path
from .views import UploadDocumentAPIView, ExtractTextAPIView


urlpatterns = [
    path(
        'upload/',
        UploadDocumentAPIView.as_view()
    ),
    path(
        'extract/<int:document_id>/',
        ExtractTextAPIView.as_view()
    ),
]