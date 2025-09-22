"""Test application startup with external services stubbed."""

from __future__ import annotations

import importlib
import sys
import types
from typing import Dict

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch):
    """Provide FastAPI app with external dependencies stubbed."""

    # Provide required environment variables so settings can load.
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("GLOBAL_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("GLOBAL_SUPABASE_ANON_KEY", "anon-key")
    monkeypatch.setenv("GLOBAL_SUPABASE_SERVICE_ROLE_KEY", "service-role")
    monkeypatch.setenv("TENANT_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("TENANT_SUPABASE_ANON_KEY", "anon-key")
    monkeypatch.setenv("TENANT_SUPABASE_SERVICE_ROLE_KEY", "service-role")
    monkeypatch.setenv("TENANT_SUPABASE_JWT_SECRET", "jwt-secret")
    monkeypatch.setenv("OFFLINE_MODE", "true")

    # Stub the queue service so startup background tasks do not require Supabase.
    queue_service_stub = types.ModuleType("services.queue_service")

    async def fake_start_queue_workers() -> None:
        return None

    class DummyQueueService:
        async def enqueue_export_job(self, *_, **__) -> Dict[str, str]:
            return {
                "job_id": "test-job",
                "status": "queued",
                "status_url": "/api/v1/export/status/test-job",
            }

        async def process_export_queue(self) -> None:
            return None

    queue_service_stub.start_queue_workers = fake_start_queue_workers  # type: ignore[attr-defined]
    queue_service_stub.queue_service = DummyQueueService()  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "services.queue_service", queue_service_stub)

    # Ensure fresh modules using the stubbed dependencies.
    for module_name in [
        "config.settings",
        "backend.main",
    ]:
        if module_name in sys.modules:
            del sys.modules[module_name]

    settings_module = importlib.import_module("config.settings")
    importlib.reload(settings_module)

    backend_main = importlib.import_module("backend.main")
    monkeypatch.setattr(
        backend_main.supabase_manager,
        "health_check",
        lambda: {"global_rag": True, "tenant_rag": True},
    )

    return backend_main.app


def test_health_endpoint_returns_healthy(app) -> None:
    """The health endpoint should respond successfully after startup."""
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
