"""
Configurações centralizadas da aplicação AWS SWF.

Este módulo gerencia todas as configurações necessárias para a execução
do workflow, incluindo credenciais AWS, timeouts e identificadores.
"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    """
    Classe de configuração centralizada para o workflow AWS SWF.
    
    Todas as configurações são carregadas de variáveis de ambiente
    para facilitar a gestão em diferentes ambientes (dev, staging, prod).
    """
    
    # ========== Credenciais AWS ==========
    # Credenciais de acesso à AWS - NUNCA commitar valores reais
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # ========== Configurações do SWF ==========
    # Domain: namespace lógico para workflows e atividades
    SWF_DOMAIN = os.getenv('SWF_DOMAIN', 'business-process-domain')
    
    # Task List: fila onde workers buscam tarefas para executar
    SWF_TASK_LIST = os.getenv('SWF_TASK_LIST', 'business-process-tasks')
    
    # ========== Configurações do Workflow ==========
    # Nome e versão do tipo de workflow
    WORKFLOW_NAME = 'BusinessProcessWorkflow'
    WORKFLOW_VERSION = '1.0'
    
    # ========== Configurações de Atividades ==========
    # Versão das atividades (permite versionamento independente)
    ACTIVITY_VERSION = '1.0'
    
    # Timeout para execução de uma atividade (5 minutos)
    ACTIVITY_TASK_TIMEOUT = '300'
    
    # Timeout total desde o agendamento até conclusão (10 minutos)
    ACTIVITY_SCHEDULE_TO_CLOSE_TIMEOUT = '600'
    
    # Timeout para uma atividade começar após ser agendada (5 minutos)
    ACTIVITY_SCHEDULE_TO_START_TIMEOUT = '300'
    
    # Timeout para uma atividade completar após iniciar (5 minutos)
    ACTIVITY_START_TO_CLOSE_TIMEOUT = '300'
    
    # ========== Configurações de Decision Tasks ==========
    # Timeout para processar uma decision task (5 minutos)
    DECISION_TASK_TIMEOUT = '300'
    
    # Timeout total para execução completa do workflow (1 hora)
    EXECUTION_START_TO_CLOSE_TIMEOUT = '3600'
