from __future__ import annotations

from django.db import models


class Note(models.Model):
    """A minimal model to validate local DB + migrations."""

    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover
        return self.title