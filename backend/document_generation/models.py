from django.conf import settings
from django.db import models


class GeneratedDocument(models.Model):
    """A draft produced by the generator (powers the 'Recent Drafts' panel)."""

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("completed", "Completed"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="generated_documents",
    )
    title = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=64, blank=True)
    language = models.CharField(max_length=32, default="English")
    content = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="completed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title
