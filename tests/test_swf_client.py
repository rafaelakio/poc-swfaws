"""Testes do SWFClient usando moto para mockar o AWS SWF."""

from __future__ import annotations

import pytest

moto = pytest.importorskip("moto")
from moto import mock_aws  # noqa: E402


@pytest.fixture
def swf_client_module():
    import importlib

    import config
    import swf_client

    importlib.reload(config)
    importlib.reload(swf_client)
    return swf_client


@mock_aws
def test_register_domain_cria_dominio(swf_client_module):
    client = swf_client_module.SWFClient()
    client.register_domain()

    response = client.client.list_domains(registrationStatus="REGISTERED")
    nomes = [d["name"] for d in response["domainInfos"]]
    assert client.domain in nomes


@mock_aws
def test_register_workflow_type(swf_client_module):
    client = swf_client_module.SWFClient()
    client.register_domain()
    client.register_workflow_type()

    response = client.client.list_workflow_types(
        domain=client.domain, registrationStatus="REGISTERED"
    )
    nomes = [wt["workflowType"]["name"] for wt in response["typeInfos"]]
    assert "BusinessProcessWorkflow" in nomes


@mock_aws
def test_register_workflow_type_define_task_list_e_nome(swf_client_module):
    client = swf_client_module.SWFClient()
    client.register_domain()
    client.register_workflow_type()

    response = client.client.describe_workflow_type(
        domain=client.domain,
        workflowType={"name": "BusinessProcessWorkflow", "version": "1.0"},
    )
    config = response["configuration"]
    assert config["defaultTaskList"]["name"] == client.task_list
