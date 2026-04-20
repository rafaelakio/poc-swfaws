"""Configuração global da suíte de testes.

Define variáveis de ambiente AWS falsas para que boto3/moto não tentem
usar credenciais reais ou a ~/.aws/credentials durante os testes.
"""

from __future__ import annotations

import os

import pytest

# Garante credenciais AWS falsas antes de qualquer import de boto3/moto
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_SESSION_TOKEN", "testing")
os.environ.setdefault("AWS_SECURITY_TOKEN", "testing")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("SWF_DOMAIN", "test-domain")
os.environ.setdefault("SWF_TASK_LIST", "test-task-list")


@pytest.fixture(autouse=True)
def _aws_env_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reforça env vars fake em todos os testes."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("SWF_DOMAIN", "test-domain")
    monkeypatch.setenv("SWF_TASK_LIST", "test-task-list")
