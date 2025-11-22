"""
Cliente AWS SWF para gerenciamento de domínios e tipos de workflow.

Este módulo fornece uma interface simplificada para interagir com o
AWS Simple Workflow Service, incluindo registro de domínios e workflows.
"""

import boto3
from config import Config

class SWFClient:
    """
    Cliente para interação com AWS SWF.
    
    Encapsula a configuração do cliente boto3 e fornece métodos
    para registrar recursos necessários no SWF.
    """
    
    def __init__(self):
        """
        Inicializa o cliente SWF com credenciais da configuração.
        
        Cria uma instância do cliente boto3 configurado com as
        credenciais AWS e região especificadas no Config.
        """
        # Inicializa o cliente boto3 para SWF
        self.client = boto3.client(
            'swf',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.AWS_REGION
        )
        
        # Armazena configurações frequentemente usadas
        self.domain = Config.SWF_DOMAIN
        self.task_list = Config.SWF_TASK_LIST
    
    def register_domain(self):
        """
        Registra o domínio SWF se ainda não existir.
        
        Um domínio é um namespace lógico que agrupa workflows e atividades
        relacionados. O período de retenção define por quanto tempo o
        histórico de execução será mantido (30 dias neste caso).
        
        Raises:
            Exception: Se houver erro na comunicação com AWS (exceto domínio já existente)
        """
        try:
            self.client.register_domain(
                name=self.domain,
                workflowExecutionRetentionPeriodInDays='30',  # Histórico mantido por 30 dias
                description='Domain for business process workflows'
            )
            print(f"Domain '{self.domain}' registered successfully")
        except self.client.exceptions.DomainAlreadyExistsException:
            # Domínio já existe, não é um erro
            print(f"Domain '{self.domain}' already exists")
    
    def register_workflow_type(self):
        """
        Registra o tipo de workflow se ainda não existir.
        
        Um tipo de workflow define a estrutura e configurações padrão
        para execuções de workflow. Inclui timeouts, task list padrão
        e política para workflows filhos.
        
        Raises:
            Exception: Se houver erro na comunicação com AWS (exceto tipo já existente)
        """
        try:
            self.client.register_workflow_type(
                domain=self.domain,
                name=Config.WORKFLOW_NAME,
                version=Config.WORKFLOW_VERSION,
                defaultTaskList={'name': self.task_list},  # Fila padrão para decision tasks
                defaultExecutionStartToCloseTimeout=Config.EXECUTION_START_TO_CLOSE_TIMEOUT,
                defaultTaskStartToCloseTimeout=Config.DECISION_TASK_TIMEOUT,
                defaultChildPolicy='TERMINATE',  # Termina workflows filhos se o pai terminar
                description='Bidirectional business process workflow with reprocessing capabilities'
            )
            print(f"Workflow type '{Config.WORKFLOW_NAME}' registered successfully")
        except self.client.exceptions.TypeAlreadyExistsException:
            # Tipo de workflow já existe, não é um erro
            print(f"Workflow type '{Config.WORKFLOW_NAME}' already exists")
