"""
Workflow Starter - Iniciador e controlador de workflows.

Este módulo fornece funcionalidades para iniciar, controlar e monitorar
execuções de workflow, incluindo sinais, histórico e retomada de etapas.
"""

import json
import time
import uuid
from swf_client import SWFClient
from config import Config

class WorkflowStarter:
    """
    Classe para iniciar e gerenciar execuções de workflow.
    
    Fornece métodos para:
    - Iniciar novas execuções de workflow
    - Enviar sinais para workflows em execução
    - Consultar histórico de execução
    - Terminar workflows
    - Retomar workflows a partir de etapas específicas
    """
    
    def __init__(self):
        """Inicializa o WorkflowStarter com cliente SWF."""
        self.swf_client = SWFClient()
    
    def start_workflow(self, workflow_input):
        """
        Inicia uma nova execução de workflow.
        
        Cria uma nova instância do workflow com um ID único e
        envia os dados de entrada para processamento.
        
        Args:
            workflow_input (dict): Dados de entrada para o workflow
                Exemplo: {'order_id': 'ORD-123', 'items': [...]}
        
        Returns:
            dict: Contém workflow_id e run_id da execução iniciada
            
        Raises:
            Exception: Se houver erro ao iniciar o workflow
        """
        # Gera um ID único para esta execução
        workflow_id = f"workflow-{uuid.uuid4()}"
        
        try:
            # Inicia a execução do workflow no SWF
            response = self.swf_client.client.start_workflow_execution(
                domain=self.swf_client.domain,
                workflowId=workflow_id,  # Identificador único do workflow
                workflowType={
                    'name': Config.WORKFLOW_NAME,
                    'version': Config.WORKFLOW_VERSION
                },
                taskList={'name': self.swf_client.task_list},  # Fila para decision tasks
                input=json.dumps(workflow_input),  # Dados de entrada serializados
                executionStartToCloseTimeout=Config.EXECUTION_START_TO_CLOSE_TIMEOUT,
                taskStartToCloseTimeout=Config.DECISION_TASK_TIMEOUT,
                childPolicy='TERMINATE'  # Política para workflows filhos
            )
            
            # Extrai o run_id da resposta (identificador único desta execução)
            run_id = response['runId']
            print(f"Workflow started successfully!")
            print(f"Workflow ID: {workflow_id}")
            print(f"Run ID: {run_id}")
            
            return {
                'workflow_id': workflow_id,
                'run_id': run_id
            }
            
        except Exception as e:
            print(f"Error starting workflow: {e}")
            raise
    
    def signal_workflow(self, workflow_id, run_id, signal_name, signal_input):
        """
        Envia um sinal para um workflow em execução.
        
        Sinais permitem comunicação externa com workflows em execução,
        útil para pausar, retomar ou alterar o comportamento do workflow.
        
        Args:
            workflow_id (str): ID do workflow
            run_id (str): ID da execução específica
            signal_name (str): Nome do sinal (ex: 'PAUSE', 'RESUME_FROM_STEP')
            signal_input (dict): Dados adicionais do sinal
            
        Raises:
            Exception: Se houver erro ao enviar o sinal
        """
        try:
            self.swf_client.client.signal_workflow_execution(
                domain=self.swf_client.domain,
                workflowId=workflow_id,
                runId=run_id,
                signalName=signal_name,
                input=json.dumps(signal_input)
            )
            print(f"Signal '{signal_name}' sent to workflow {workflow_id}")
        except Exception as e:
            print(f"Error sending signal: {e}")
            raise
    
    def get_workflow_history(self, workflow_id, run_id):
        """
        Obtém o histórico completo de eventos de um workflow.
        
        Recupera todos os eventos que ocorreram durante a execução,
        incluindo início, atividades agendadas, completadas, falhas, etc.
        Útil para debugging e auditoria.
        
        Args:
            workflow_id (str): ID do workflow
            run_id (str): ID da execução específica
            
        Returns:
            list: Lista completa de eventos do workflow
            
        Raises:
            Exception: Se houver erro ao obter o histórico
        """
        try:
            events = []
            next_page_token = None
            
            # Itera sobre todas as páginas de eventos (paginação automática)
            while True:
                params = {
                    'domain': self.swf_client.domain,
                    'execution': {
                        'workflowId': workflow_id,
                        'runId': run_id
                    }
                }
                
                # Adiciona token de paginação se houver mais páginas
                if next_page_token:
                    params['nextPageToken'] = next_page_token
                
                response = self.swf_client.client.get_workflow_execution_history(**params)
                events.extend(response['events'])
                
                # Se não há mais páginas, termina o loop
                if 'nextPageToken' not in response:
                    break
                
                next_page_token = response['nextPageToken']
            
            return events
            
        except Exception as e:
            print(f"Error getting workflow history: {e}")
            raise
    
    def terminate_workflow(self, workflow_id, run_id, reason="Manual termination"):
        """
        Termina forçadamente um workflow em execução.
        
        Interrompe imediatamente a execução do workflow.
        Use com cuidado, pois não permite cleanup ou compensação.
        
        Args:
            workflow_id (str): ID do workflow
            run_id (str): ID da execução específica
            reason (str): Motivo da terminação (para auditoria)
            
        Raises:
            Exception: Se houver erro ao terminar o workflow
        """
        try:
            self.swf_client.client.terminate_workflow_execution(
                domain=self.swf_client.domain,
                workflowId=workflow_id,
                runId=run_id,
                reason=reason
            )
            print(f"Workflow {workflow_id} terminated")
        except Exception as e:
            print(f"Error terminating workflow: {e}")
            raise
    
    def resume_workflow_from_step(self, workflow_id, run_id, step_name):
        """
        Retoma um workflow a partir de uma etapa específica.
        
        Permite reprocessamento a partir de qualquer etapa do workflow.
        Útil quando uma etapa falhou e foi corrigida manualmente,
        ou quando é necessário reprocessar parte do fluxo.
        
        Args:
            workflow_id (str): ID do workflow
            run_id (str): ID da execução específica
            step_name (str): Nome da etapa para retomar
                Exemplos: 'ValidateInput', 'ProcessData', 'EnrichData'
        """
        # Prepara dados do sinal de retomada
        signal_input = {
            'action': 'RESUME_FROM_STEP',
            'step': step_name,
            'timestamp': time.time()
        }
        
        # Envia sinal para o workflow
        self.signal_workflow(workflow_id, run_id, 'RESUME_FROM_STEP', signal_input)
        print(f"Workflow will resume from step: {step_name}")

if __name__ == '__main__':
    starter = WorkflowStarter()
    
    # Exemplo de uso
    workflow_input = {
        'order_id': 'ORD-12345',
        'items': ['item1', 'item2', 'item3'],
        'customer_id': 'CUST-789'
    }
    
    result = starter.start_workflow(workflow_input)
    print(f"\nWorkflow execution details: {result}")
