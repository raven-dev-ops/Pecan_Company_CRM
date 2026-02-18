"""Azure integration boundary.

This module is intentionally a stub.

Replace `AzureClientStub` with a real implementation later (e.g. Azure SQL,
Storage, Service Bus, etc.). Keep imports of Azure SDKs inside the real
implementation so local runs don't require Azure dependencies.
"""

from __future__ import annotations


class AzureNotConfigured(RuntimeError):
    """Raised when Azure integration is called before being implemented."""


class AzureClientStub:
    def ping(self) -> bool:
        """Used for quick smoke-tests."""
        return False

    def __getattr__(self, name: str):
        raise AzureNotConfigured(
            f"Azure integration is not configured (attempted to access: {name}). "
            "Implement integrations/azure.py and enable it via AZURE_ENABLED=1."
        )