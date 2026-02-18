from __future__ import annotations

from django.http import JsonResponse


def health(request):
    """Simple health check endpoint for local run validation."""
    return JsonResponse({"status": "ok"})