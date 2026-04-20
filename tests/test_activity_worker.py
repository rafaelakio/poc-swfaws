"""Testes das atividades de negócio e do registro via moto."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

moto = pytest.importorskip("moto")
from moto import mock_aws  # noqa: E402


@pytest.fixture
def worker_module():
    import importlib

    import activity_worker
    import config
    import swf_client

    importlib.reload(config)
    importlib.reload(swf_client)
    importlib.reload(activity_worker)
    return activity_worker


def test_validate_input_sucesso(worker_module):
    worker = worker_module.ActivityWorker()
    resultado = worker.validate_input({"order_id": "ORD-1"})
    assert resultado["status"] == "validated"
    assert resultado["order_id"] == "ORD-1"
    assert "validated_at" in resultado


def test_validate_input_falha_sem_order_id(worker_module):
    worker = worker_module.ActivityWorker()
    with pytest.raises(Exception, match="Missing order_id"):
        worker.validate_input({})


def test_process_data_retorna_itens(worker_module, monkeypatch):
    monkeypatch.setattr(worker_module.time, "sleep", lambda _s: None)
    worker = worker_module.ActivityWorker()
    resultado = worker.process_data({"order_id": "X", "items": [1, 2, 3]})
    assert resultado["status"] == "processed"
    assert resultado["processed_items"] == [1, 2, 3]


def test_enrich_data(worker_module, monkeypatch):
    monkeypatch.setattr(worker_module.time, "sleep", lambda _s: None)
    worker = worker_module.ActivityWorker()
    resultado = worker.enrich_data({"order_id": "X"})
    assert resultado["status"] == "enriched"
    assert resultado["enriched_data"]["customer_tier"] == "premium"


def test_handle_activity_task_sucesso_usa_taskToken(worker_module):
    worker = worker_module.ActivityWorker()
    worker.swf_client.client = MagicMock()

    task = {
        "taskToken": "tok-123",
        "activityType": {"name": "ValidateInput", "version": "1.0"},
        "input": json.dumps({"order_id": "ORD-42"}),
    }
    worker.handle_activity_task(task)

    worker.swf_client.client.respond_activity_task_completed.assert_called_once()
    kwargs = worker.swf_client.client.respond_activity_task_completed.call_args.kwargs
    assert kwargs["taskToken"] == "tok-123"
    payload = json.loads(kwargs["result"])
    assert payload["status"] == "validated"
    assert payload["order_id"] == "ORD-42"


def test_handle_activity_task_falha_reporta_respond_activity_task_failed(worker_module):
    worker = worker_module.ActivityWorker()
    worker.swf_client.client = MagicMock()

    task = {
        "taskToken": "tok-err",
        "activityType": {"name": "ValidateInput", "version": "1.0"},
        "input": json.dumps({}),  # sem order_id → falha
    }
    worker.handle_activity_task(task)

    worker.swf_client.client.respond_activity_task_failed.assert_called_once()
    kwargs = worker.swf_client.client.respond_activity_task_failed.call_args.kwargs
    assert kwargs["taskToken"] == "tok-err"
    assert "order_id" in kwargs["reason"]


def test_handle_activity_task_desconhecida(worker_module):
    worker = worker_module.ActivityWorker()
    worker.swf_client.client = MagicMock()

    task = {
        "taskToken": "tok-unk",
        "activityType": {"name": "AtividadeInexistente", "version": "1.0"},
        "input": json.dumps({}),
    }
    worker.handle_activity_task(task)

    worker.swf_client.client.respond_activity_task_failed.assert_called_once()


@mock_aws
def test_register_activities_cria_todos_os_tipos(worker_module):
    worker = worker_module.ActivityWorker()
    worker.swf_client.register_domain()
    worker.register_activities()

    response = worker.swf_client.client.list_activity_types(
        domain=worker.swf_client.domain, registrationStatus="REGISTERED"
    )
    registrados = {info["activityType"]["name"] for info in response["typeInfos"]}
    assert set(worker.activities.keys()) <= registrados
