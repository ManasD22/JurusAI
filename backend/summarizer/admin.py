from django.contrib import admin

from .models import DocumentSummary


@admin.register(DocumentSummary)
class DocumentSummaryAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "original_filename", "created_at")
    search_fields = ("title", "original_filename", "user__username")
