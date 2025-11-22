"""
Activity Worker - Executor de atividades do workflow.

Este módulo implementa o worker que executa as atividades de negócio
do workflow. Ele faz polling na task list, executa as atividades
e reporta os resultados de volta ao SWF.
"""

import json
import time
from swf_client import SWFClient
from config import Config

class ActivityWorker:
    """
    Worker responsável por executar atividades do workflow.
    
    O Activity Worker:
    1. Registra todas as atividades disponíveis no SWF
    2. Faz polling contínuo por tarefas na task list
    3. Executa a lógica de negócio de cada atividade
    4. Reporta sucesso ou falha de volta ao SWF
    """
    def __init__(self):
        """
        Inicializa o Activity Worker.
        
        Cria uma instância do cliente SWF e mapeia nomes de atividades
        para seus métodos de implementação correspondentes.
        """
        self.swf_client = SWFClient()
        
        # Mapeamento de nomes de atividades para métodos de implementação
        # Permite adicionar novas atividades facilmente
        self.activities = {
            'ValidateInput': self.validate_input,           # Valida dados de entrada
            'ProcessData': self.process_data,               # Processa dados principais
            'EnrichData': self.enrich_data,                 # Enriquece com dados adicionais
            'SaveResults': self.save_results,               # Persiste resultados
            'NotifyCompletion': self.notify_completion,     # Notifica conclusão
            'RollbackStep': self.rollback_step,             # Reverte uma etapa
            'CompensateTransaction': self.compensate_transaction  # Compensa transação (SAGA)
        }
    
    def register_activities(self):
        """
        Registra todas as atividades do workflow no SWF.
        
        Cada atividade precisa ser registrada antes de poder ser agendada
        pelo decision worker. Este método itera sobre todas as atividades
        mapeadas e as registra com suas configurações de timeout.
        
        Raises:
            Exception: Se houver erro na comunicação com AWS (exceto tipo já existente)
        """
        for activity_name in self.activities.keys():
            try:
                self.swf_client.client.register_activity_type(
                    domain=self.swf_client.domain,
                    name=activity_name,
                    version=Config.ACTIVITY_VERSION,
                    defaultTaskList={'name': self.swf_client.task_list},
                    defaultTaskStartToCloseTimeout=Config.ACTIVITY_TASK_TIMEOUT,
                    defaultTaskScheduleToCloseTimeout=Config.ACTIVITY_SCHEDULE_TO_CLOSE_TIMEOUT,
                    defaultTaskScheduleToStartTimeout=Config.ACTIVITY_SCHEDULE_TO_START_TIMEOUT,
                    defaultTaskHeartbeatTimeout='60',  # Heartbeat a cada 60 segundos
                    description=f'Activity: {activity_name}'
                )
                print(f"Activity '{activity_name}' registered successfully")
            except self.swf_client.client.exceptions.TypeAlreadyExistsException:
                # Atividade já registrada, não é um erro
                print(f"Activity '{activity_name}' already exists")
    
    def poll_for_activity_task(self):
        """
        Loop principal que busca e executa tarefas de atividade.
        
        Este método faz polling contínuo (long polling) na task list do SWF,
        aguardando por novas tarefas de atividade. Quando uma tarefa é recebida,
        ela é processada imediatamente.
        
        O loop continua indefinidamente até que o processo seja interrompido.
        Em caso de erro, aguarda 5 segundos antes de tentar novamente.
        """
        print(f"Polling for activity tasks on task list: {self.swf_client.task_list}")
        
        while True:
            try:
                # Long polling: aguarda até 60 segundos por uma tarefa
                response = self.swf_client.client.poll_for_activity_task(
                    domain=self.swf_client.domain,
                    taskList={'name': self.swf_client.task_list},
                    identity='activity-worker-1'  # Identificador único deste worker
                )
                
                # Se taskToken está presente, há uma tarefa para processar
                if 'taskToken' in response:
                    self.handle_activity_task(response)
                else:
                    # Nenhuma tarefa disponível no momento
                    print("No activity task available, waiting...")
                    time.sleep(2)
                    
            except Exception as e:
                print(f"Error polling for activity task: {e}")
                time.sleep(5)  # Aguarda antes de tentar novamente
    
    def handle_activity_task(self, task):
        """
        Processa uma tarefa de atividade recebida do SWF.
        
        Extrai informações da tarefa, executa a lógica de negócio correspondente
        e reporta o resultado (sucesso ou falha) de volta ao SWF.
        
        Args:
            task (dict): Objeto de tarefa retornado pelo SWF contendo:
                - taskToken: Token único para responder à tarefa
                - activityType: Tipo e versão da atividade
                - input: Dados de entrada em formato JSON
        """
        # Token necessário para responder à tarefa
        task_token = task['taskToken']
        
        # Nome da atividade a ser executada
        activity_type = task['activityType']['name']
        
        # Dados de entrada (deserializa JSON)
        input_data = json.loads(task.get('input', '{}'))
        
        print(f"\nReceived activity task: {activity_type}")
        print(f"Input: {input_data}")
        
        try:
            # Executa a atividade correspondente usando o mapeamento
            if activity_type in self.activities:
                result = self.activities[activity_type](input_data)
                
                # Reporta sucesso ao SWF com o resultado
                self.swf_client.client.respond_activity_task_completed(
                    taskToken=task_token,
                    result=json.dumps(result)
                )
                print(f"Activity '{activity_type}' completed successfully")
            else:
                raise Exception(f"Unknown activity type: {activity_type}")
                
        except Exception as e:
            # Em caso de erro, reporta falha ao SWF
            print(f"Activity '{activity_type}' failed: {e}")
            self.swf_client.client.respond_activity_task_failed(
                taskToken=task_token,
                reason=str(e)[:256],      # Motivo limitado a 256 caracteres
                details=str(e)[:32768]    # Detalhes limitados a 32KB
            )

    
    # ========== Implementação das Atividades de Negócio ==========
    
    def validate_input(self, input_data):
        """
        Valida os dados de entrada do workflow.
        
        Primeira etapa do processo que verifica se todos os dados
        obrigatórios estão presentes e válidos.
        
        Args:
            input_data (dict): Dados de entrada contendo order_id e outros campos
            
        Returns:
            dict: Resultado da validação com status e timestamp
            
        Raises:
            Exception: Se dados obrigatórios estiverem faltando
        """
        print("Executing: ValidateInput")
        
        # Verifica se order_id está presente
        if not input_data.get('order_id'):
            raise Exception("Missing order_id in input")
        
        return {
            'status': 'validated',
            'order_id': input_data['order_id'],
            'validated_at': time.time()
        }
    
    def process_data(self, input_data):
        """
        Processa os dados principais do pedido.
        
        Executa a lógica de negócio principal, como cálculos,
        transformações e validações de regras de negócio.
        
        Args:
            input_data (dict): Dados validados do pedido
            
        Returns:
            dict: Dados processados com status e itens
        """
        print("Executing: ProcessData")
        time.sleep(1)  # Simula processamento demorado
        
        return {
            'status': 'processed',
            'order_id': input_data.get('order_id'),
            'processed_items': input_data.get('items', []),
            'processed_at': time.time()
        }
    
    def enrich_data(self, input_data):
        """
        Enriquece os dados com informações adicionais.
        
        Adiciona dados complementares como informações de cliente,
        descontos aplicáveis, dados de marketing, etc.
        
        Args:
            input_data (dict): Dados processados
            
        Returns:
            dict: Dados enriquecidos com informações adicionais
        """
        print("Executing: EnrichData")
        time.sleep(1)  # Simula consulta a serviços externos
        
        return {
            'status': 'enriched',
            'order_id': input_data.get('order_id'),
            'enriched_data': {
                'customer_tier': 'premium',
                'discount_applied': True
            },
            'enriched_at': time.time()
        }
    
    def save_results(self, input_data):
        """
        Persiste os resultados do processamento.
        
        Salva os dados processados em banco de dados, storage
        ou outro sistema de persistência.
        
        Args:
            input_data (dict): Dados finais a serem salvos
            
        Returns:
            dict: Confirmação de salvamento com ID do registro
        """
        print("Executing: SaveResults")
        time.sleep(1)  # Simula operação de I/O
        
        return {
            'status': 'saved',
            'order_id': input_data.get('order_id'),
            'saved_at': time.time(),
            'record_id': f"REC-{int(time.time())}"
        }
    
    def notify_completion(self, input_data):
        """
        Notifica a conclusão do processo.
        
        Envia notificações para sistemas externos, usuários
        ou outros serviços sobre a conclusão do workflow.
        
        Args:
            input_data (dict): Dados do processo concluído
            
        Returns:
            dict: Confirmação de envio da notificação
        """
        print("Executing: NotifyCompletion")
        
        return {
            'status': 'notified',
            'order_id': input_data.get('order_id'),
            'notification_sent': True,
            'notified_at': time.time()
        }
    
    def rollback_step(self, input_data):
        """
        Reverte uma etapa específica do workflow.
        
        Implementa a lógica de rollback para desfazer operações
        de uma etapa que falhou após múltiplas tentativas.
        
        Args:
            input_data (dict): Contém step_to_rollback e dados do workflow
            
        Returns:
            dict: Confirmação do rollback executado
        """
        print("Executing: RollbackStep")
        step_to_rollback = input_data.get('step_to_rollback')
        
        # Aqui você implementaria a lógica específica de rollback
        # para cada tipo de etapa (ex: deletar registros, reverter transações)
        
        return {
            'status': 'rolled_back',
            'rolled_back_step': step_to_rollback,
            'rolled_back_at': time.time()
        }
    
    def compensate_transaction(self, input_data):
        """
        Compensa uma transação usando o padrão SAGA.
        
        Implementa transações compensatórias para manter a consistência
        eventual quando não é possível fazer rollback direto.
        
        Args:
            input_data (dict): Dados da transação a ser compensada
            
        Returns:
            dict: Confirmação da compensação executada
        """
        print("Executing: CompensateTransaction")
        
        # Implementa ações compensatórias (ex: estornar pagamento,
        # liberar recursos reservados, enviar notificações de cancelamento)
        
        return {
            'status': 'compensated',
            'order_id': input_data.get('order_id'),
            'compensated_at': time.time()
        }

if __name__ == '__main__':
    worker = ActivityWorker()
    worker.register_activities()
    worker.poll_for_activity_task()
