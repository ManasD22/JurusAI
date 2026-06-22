from django.contrib import admin

from .models import GeneratedDocument


@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "doc_type", "language", "status", "updated_at")
    list_filter = ("doc_type", "language", "status")
    search_fields = ("title", "user__username")
