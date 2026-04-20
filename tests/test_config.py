"""Testes para o módulo config."""

from __future__ import annotations

import importlib


def _reload_config():
    import config

    return importlib.reload(config)


def test_config_usa_env_vars_definidas(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "sa-east-1")
    monkeypatch.setenv("SWF_DOMAIN", "meu-dominio")
    monkeypatch.setenv("SWF_TASK_LIST", "minha-task-list")

    module = _reload_config()

    assert module.Config.AWS_REGION == "sa-east-1"
    assert module.Config.SWF_DOMAIN == "meu-dominio"
    assert module.Config.SWF_TASK_LIST == "minha-task-list"


def test_config_tem_defaults_para_workflow():
    module = _reload_config()

    assert module.Config.WORKFLOW_NAME == "BusinessProcessWorkflow"
    assert module.Config.WORKFLOW_VERSION == "1.0"
    assert module.Config.ACTIVITY_VERSION == "1.0"


def test_config_timeouts_sao_strings_numericas():
    module = _reload_config()

    for attr in [
        "ACTIVITY_TASK_TIMEOUT",
        "ACTIVITY_SCHEDULE_TO_CLOSE_TIMEOUT",
        "ACTIVITY_SCHEDULE_TO_START_TIMEOUT",
        "ACTIVITY_START_TO_CLOSE_TIMEOUT",
        "DECISION_TASK_TIMEOUT",
        "EXECUTION_START_TO_CLOSE_TIMEOUT",
    ]:
        value = getattr(module.Config, attr)
        assert isinstance(value, str)
        assert value.isdigit(), f"{attr} deve ser string numérica, obteve {value!r}"
