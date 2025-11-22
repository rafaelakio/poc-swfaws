"""
Decision Worker - Orquestrador do workflow.

Este módulo implementa o decision worker que coordena a execução do workflow.
Ele analisa o histórico de eventos, toma decisões sobre próximas ações,
gerencia retries, rollbacks e retomada de etapas.
"""

import json
import time
from swf_client import SWFClient
from config import Config

class DecisionWorker:
    """
    Worker responsável por tomar decisões no workflow.
    
    O Decision Worker:
    1. Faz polling por decision tasks
    2. Analisa o histórico completo de eventos do workflow
    3. Determina o estado atual e próximas ações
    4. Agenda atividades, gerencia retries e rollbacks
    5. Completa ou falha o workflow quando apropriado
    """
    
    def __init__(self):
        """
        Inicializa o Decision Worker.
        
        Cria instância do cliente SWF e estrutura para
        armazenar estado do workflow durante processamento.
        """
        self.swf_client = SWFClient()
        self.workflow_state = {}  # Estado temporário durante decisões
    
    def poll_for_decision_task(self):
        """
        Loop principal que busca e processa decision tasks.
        
        Este método faz polling contínuo (long polling) na task list do SWF,
        aguardando por decision tasks. Uma decision task é criada quando:
        - O workflow inicia
        - Uma atividade completa
        - Uma atividade falha
        - Um timer dispara
        - Um sinal é recebido
        
        O loop continua indefinidamente até que o processo seja interrompido.
        """
        print(f"Polling for decision tasks on task list: {self.swf_client.task_list}")
        
        while True:
            try:
                # Long polling: aguarda até 60 segundos por uma decision task
                response = self.swf_client.client.poll_for_decision_task(
                    domain=self.swf_client.domain,
                    taskList={'name': self.swf_client.task_list},
                    identity='decision-worker-1'  # Identificador único deste worker
                )
                
                # Se taskToken está presente, há uma decision task para processar
                if 'taskToken' in response:
                    self.handle_decision_task(response)
                else:
                    # Nenhuma decision task disponível no momento
                    print("No decision task available, waiting...")
                    time.sleep(2)
                    
            except Exception as e:
                print(f"Error polling for decision task: {e}")
                time.sleep(5)  # Aguarda antes de tentar novamente
    
    def handle_decision_task(self, task):
        """
        Processa uma decision task recebida do SWF.
        
        Analisa todo o histórico de eventos do workflow para determinar
        o estado atual e toma decisões sobre as próximas ações.
        
        Args:
            task (dict): Objeto de decision task contendo:
                - taskToken: Token único para responder
                - events: Lista completa de eventos do workflow
                - workflowExecution: Identificadores do workflow
        """
        # Token necessário para responder à decision task
        task_token = task['taskToken']
        
        # Histórico completo de eventos do workflow
        events = task['events']
        
        # Identificadores do workflow (workflowId e runId)
        workflow_execution = task['workflowExecution']
        
        print(f"\nReceived decision task for workflow: {workflow_execution['workflowId']}")
        
        # Analisa o histórico de eventos para determinar estado atual
        state = self.analyze_events(events)
        
        # Toma decisões baseadas no estado (agenda atividades, completa workflow, etc)
        decisions = self.make_decisions(state)
        
        # Responde ao SWF com as decisões tomadas
        try:
            self.swf_client.client.respond_decision_task_completed(
                taskToken=task_token,
                decisions=decisions  # Lista de decisões a serem executadas
            )
            print(f"Decision task completed with {len(decisions)} decision(s)")
        except Exception as e:
            print(f"Error responding to decision task: {e}")
    
    def analyze_events(self, events):
        """
        Analisa o histórico de eventos para determinar o estado atual do workflow.
        
        Percorre todos os eventos do workflow e constrói uma representação
        do estado atual, incluindo atividades completadas, falhas, retries
        e marcadores especiais.
        
        Args:
            events (list): Lista completa de eventos do workflow
            
        Returns:
            dict: Estado atual do workflow contendo:
                - completed_activities: Lista de atividades concluídas
                - failed_activities: Lista de atividades que falharam
                - workflow_input: Dados de entrada do workflow
                - activity_results: Resultados de cada atividade
                - retry_count: Contador de tentativas por atividade
                - markers: Marcadores especiais (rollback, resume, etc)
        """
        # Inicializa estrutura de estado
        state = {
            'completed_activities': [],   # Atividades concluídas com sucesso
            'failed_activities': [],      # Atividades que falharam
            'current_step': 0,            # Etapa atual do workflow
            'workflow_input': {},         # Input original do workflow
            'activity_results': {},       # Resultados de cada atividade
            'should_retry': False,        # Flag para indicar retry
            'should_rollback': False,     # Flag para indicar rollback
            'retry_count': {},            # Contador de retries por atividade
            'markers': {}                 # Marcadores especiais do workflow
        }
        
        # Percorre todos os eventos em ordem cronológica
        for event in events:
            event_type = event['eventType']
            
            # Evento de início do workflow - captura input
            if event_type == 'WorkflowExecutionStarted':
                attrs = event['workflowExecutionStartedEventAttributes']
                state['workflow_input'] = json.loads(attrs.get('input', '{}'))
            
            # Evento de atividade completada - registra sucesso
            elif event_type == 'ActivityTaskCompleted':
                attrs = event['activityTaskCompletedEventAttributes']
                # Busca o evento de agendamento para obter o nome da atividade
                scheduled_event = next(
                    e for e in events 
                    if e['eventId'] == attrs['scheduledEventId']
                )
                activity_name = scheduled_event['activityTaskScheduledEventAttributes']['activityType']['name']
                state['completed_activities'].append(activity_name)
                state['activity_results'][activity_name] = json.loads(attrs.get('result', '{}'))
            
            # Evento de atividade falhada - registra falha e incrementa retry
            elif event_type == 'ActivityTaskFailed':
                attrs = event['activityTaskFailedEventAttributes']
                # Busca o evento de agendamento para obter o nome da atividade
                scheduled_event = next(
                    e for e in events 
                    if e['eventId'] == attrs['scheduledEventId']
                )
                activity_name = scheduled_event['activityTaskScheduledEventAttributes']['activityType']['name']
                state['failed_activities'].append(activity_name)
                
                # Incrementa contador de retry para esta atividade
                if activity_name not in state['retry_count']:
                    state['retry_count'][activity_name] = 0
                state['retry_count'][activity_name] += 1
            
            # Evento de marcador - usado para controle de fluxo especial
            elif event_type == 'MarkerRecorded':
                attrs = event['markerRecordedEventAttributes']
                marker_name = attrs['markerName']
                state['markers'][marker_name] = json.loads(attrs.get('details', '{}'))
        
        return state

    
    def make_decisions(self, state):
        """
        Toma decisões baseadas no estado atual do workflow.
        
        Este é o "cérebro" do workflow que implementa a lógica de orquestração:
        - Fluxo normal: agenda próxima atividade na sequência
        - Falhas: implementa retry automático (até 3 tentativas)
        - Rollback: após max retries, inicia processo de compensação
        - Retomada: permite retomar de uma etapa específica
        
        Args:
            state (dict): Estado atual do workflow
            
        Returns:
            list: Lista de decisões a serem executadas pelo SWF
        """
        decisions = []
        
        # Define a sequência de etapas do processo de negócio
        # Esta é a ordem normal de execução do workflow
        workflow_steps = [
            'ValidateInput',      # 1. Valida entrada
            'ProcessData',        # 2. Processa dados
            'EnrichData',         # 3. Enriquece informações
            'SaveResults',        # 4. Persiste resultados
            'NotifyCompletion'    # 5. Notifica conclusão
        ]
        
        # ========== Tratamento de Falhas e Retry ==========
        # Verifica se há atividades que falharam
        if state['failed_activities']:
            last_failed = state['failed_activities'][-1]
            retry_count = state['retry_count'].get(last_failed, 0)
            
            # Implementa retry automático até 3 tentativas
            if retry_count < 3:
                print(f"Retrying activity: {last_failed} (attempt {retry_count + 1})")
                decisions.append(self.schedule_activity(last_failed, state))
                return decisions
            else:
                # Após 3 tentativas, inicia processo de rollback
                print(f"Max retries reached for {last_failed}, initiating rollback")
                
                # Registra marcador de rollback para rastreamento
                decisions.append(self.record_marker('ROLLBACK_INITIATED', {
                    'failed_activity': last_failed,
                    'reason': 'Max retries exceeded'
                }))
                
                # Agenda atividade de rollback
                decisions.append(self.schedule_activity('RollbackStep', {
                    'step_to_rollback': last_failed,
                    'workflow_input': state['workflow_input']
                }))
                return decisions
        
        # ========== Processo de Rollback e Compensação ==========
        # Verifica se está em modo de rollback (padrão SAGA)
        if 'ROLLBACK_INITIATED' in state['markers']:
            if 'RollbackStep' in state['completed_activities']:
                # Rollback concluído, agora compensa a transação
                print("Rollback completed, starting compensation")
                decisions.append(self.schedule_activity('CompensateTransaction', state['workflow_input']))
                return decisions
            elif 'CompensateTransaction' in state['completed_activities']:
                # Compensação concluída, finaliza o workflow com falha
                print("Compensation completed, failing workflow")
                decisions.append({
                    'decisionType': 'FailWorkflowExecution',
                    'failWorkflowExecutionDecisionAttributes': {
                        'reason': 'Workflow failed and compensated',
                        'details': json.dumps(state['markers']['ROLLBACK_INITIATED'])
                    }
                })
                return decisions
        
        # ========== Retomada de Etapa Específica ==========
        # Permite retomar o workflow a partir de uma etapa específica
        # Útil para reprocessamento após correção de problemas
        if 'RESUME_FROM_STEP' in state['markers']:
            resume_step = state['markers']['RESUME_FROM_STEP'].get('step')
            if resume_step in workflow_steps:
                print(f"Resuming workflow from step: {resume_step}")
                decisions.append(self.schedule_activity(resume_step, state))
                decisions.append(self.record_marker('RESUME_COMPLETED', {'resumed_step': resume_step}))
                return decisions
        
        # ========== Fluxo Normal de Execução ==========
        # Executa a próxima etapa na sequência que ainda não foi completada
        for step in workflow_steps:
            if step not in state['completed_activities']:
                print(f"Scheduling next activity: {step}")
                decisions.append(self.schedule_activity(step, state))
                return decisions
        
        # ========== Conclusão do Workflow ==========
        # Todas as etapas foram concluídas com sucesso
        print("All activities completed successfully, completing workflow")
        decisions.append({
            'decisionType': 'CompleteWorkflowExecution',
            'completeWorkflowExecutionDecisionAttributes': {
                'result': json.dumps({
                    'status': 'completed',
                    'results': state['activity_results']
                })
            }
        })
        
        return decisions
    
    def schedule_activity(self, activity_name, state):
        """
        Cria uma decisão para agendar uma atividade.
        
        Prepara todos os parâmetros necessários para agendar uma atividade,
        incluindo input, timeouts e identificadores únicos.
        
        Args:
            activity_name (str): Nome da atividade a ser agendada
            state (dict): Estado atual do workflow
            
        Returns:
            dict: Decisão de agendamento de atividade formatada para o SWF
        """
        # Prepara o input para a atividade
        activity_input = state.get('workflow_input', {}) if isinstance(state, dict) else state
        
        # Adiciona resultados de atividades anteriores se disponível
        # Permite que atividades acessem dados de etapas anteriores
        if isinstance(state, dict) and 'activity_results' in state:
            activity_input = {
                **activity_input,
                'previous_results': state['activity_results']
            }
        
        return {
            'decisionType': 'ScheduleActivityTask',
            'scheduleActivityTaskDecisionAttributes': {
                'activityType': {
                    'name': activity_name,
                    'version': Config.ACTIVITY_VERSION
                },
                # ID único para esta instância da atividade
                'activityId': f"{activity_name}-{int(time.time() * 1000)}",
                'input': json.dumps(activity_input),
                # Timeouts para controle de execução
                'scheduleToCloseTimeout': Config.ACTIVITY_SCHEDULE_TO_CLOSE_TIMEOUT,
                'scheduleToStartTimeout': Config.ACTIVITY_SCHEDULE_TO_START_TIMEOUT,
                'startToCloseTimeout': Config.ACTIVITY_START_TO_CLOSE_TIMEOUT,
                'taskList': {'name': self.swf_client.task_list},
                'heartbeatTimeout': '60'  # Worker deve enviar heartbeat a cada 60s
            }
        }
    
    def record_marker(self, marker_name, details):
        """
        Cria uma decisão para registrar um marcador no histórico.
        
        Marcadores são eventos especiais usados para controle de fluxo
        e rastreamento de estados especiais (rollback, resume, etc).
        
        Args:
            marker_name (str): Nome do marcador
            details (dict): Detalhes adicionais do marcador
            
        Returns:
            dict: Decisão de registro de marcador formatada para o SWF
        """
        return {
            'decisionType': 'RecordMarker',
            'recordMarkerDecisionAttributes': {
                'markerName': marker_name,
                'details': json.dumps(details)
            }
        }

if __name__ == '__main__':
    worker = DecisionWorker()
    worker.poll_for_decision_task()
