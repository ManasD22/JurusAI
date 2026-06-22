from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def api_root(_request):
    """Tiny landing endpoint so hitting the server root is informative."""
    return JsonResponse(
        {
            "service": "JurisAI API",
            "status": "ok",
            "endpoints": {
                "auth": "/api/auth/",
                "files": "/api/files/",
                "chatbot": "/api/chatbot/",
                "summarizer": "/api/summarizer/",
                "documents": "/api/documents/",
                "clauses": "/api/clauses/",
                "admin": "/admin/",
            },
        }
    )


urlpatterns = [
    path("", api_root),
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    path("api/files/", include("file_manager.urls")),
    path("api/chatbot/", include("chatbot.urls")),
    path("api/summarizer/", include("summarizer.urls")),
    path("api/documents/", include("document_generation.urls")),
    path("api/clauses/", include("clause_verification.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
