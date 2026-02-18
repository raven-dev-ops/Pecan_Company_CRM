"""Legacy integration boundary.

This module is intentionally a stub.

The intent is to isolate anything "legacy" (ODBC, proprietary SDKs, network shares,
SOAP, etc.) behind a small interface so the Django app and tests can run locally
without those dependencies.
"""

from __future__ import annotations


class LegacyNotConfigured(RuntimeError):
    """Raised when legacy integration is called before being implemented."""


class LegacyClientStub:
    def ping(self) -> bool:
        """Used for quick smoke-tests."""
        return False

    def __getattr__(self, name: str):
        raise LegacyNotConfigured(
            f"Legacy integration is not configured (attempted to access: {name}). "
            "Implement integrations/legacy.py and enable it via LEGACY_ENABLED=1."
        )