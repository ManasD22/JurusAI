from django.conf import settings
from django.db import models


class DocumentSummary(models.Model):
    """Stored result of a summarization run (powers history if needed)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="summaries",
    )
    title = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
