# Exemplos de Uso

Este documento contém exemplos práticos de como usar a aplicação AWS SWF.

## Exemplo 1: Workflow Simples

### Cenário
Processar um pedido de e-commerce do início ao fim.

### Código

```python
from workflow_starter import WorkflowStarter

# Inicializa o starter
starter = WorkflowStarter()

# Dados do pedido
order_data = {
    'order_id': 'ORD-2024-001',
    'customer_id': 'CUST-12345',
    'items': [
        {'sku': 'PROD-001', 'quantity': 2, 'price': 99.90},
        {'sku': 'PROD-002', 'quantity': 1, 'price': 149.90}
    ],
    'total': 349.70,
    'payment_method': 'credit_card'
}

# Inicia o workflow
result = starter.start_workflow(order_data)

print(f"Pedido {order_data['order_id']} em processamento")
print(f"Workflow ID: {result['workflow_id']}")
print(f"Run ID: {result['run_id']}")
```

### Saída Esperada

```
Pedido ORD-2024-001 em processamento
Workflow ID: workflow-a1b2c3d4-e5f6-7890-abcd-ef1234567890
Run ID: 12345678-90ab-cdef-1234-567890abcdef
```

## Exemplo 2: Tratamento de Falha com Retry

### Cenário
Uma atividade falha temporariamente (ex: serviço externo indisponível).

### Comportamento

```
Tentativa 1: ProcessData → FALHA (timeout)
Tentativa 2: ProcessData → FALHA (timeout)
Tentativa 3: ProcessData → SUCESSO
Continua: EnrichData → ...
```

### Logs do Decision Worker

```
Received decision task for workflow: workflow-abc-123
Activity 'ProcessData' failed: Connection timeout
Retrying activity: ProcessData (attempt 2)

Received decision task for workflow: workflow-abc-123
Activity 'ProcessData' failed: Connection timeout
Retrying activity: ProcessData (attempt 3)

Received decision task for workflow: workflow-abc-123
Activity 'ProcessData' completed successfully
Scheduling next activity: EnrichData
```

## Exemplo 3: Rollback Após Falhas Persistentes

### Cenário
Atividade falha 3 vezes, iniciando processo de rollback.

### Código (não requer ação manual)

O Decision Worker automaticamente:

```python
# Após 3 falhas
if retry_count >= 3:
    # Registra marcador de rollback
    record_marker('ROLLBACK_INITIATED', {
        'failed_activity': 'SaveResults',
        'reason': 'Max retries exceeded'
    })
    
    # Agenda rollback
    schedule_activity('RollbackStep', {
        'step_to_rollback': 'SaveResults'
    })
```

### Fluxo Completo

```
ValidateInput → SUCESSO
ProcessData → SUCESSO
EnrichData → SUCESSO
SaveResults → FALHA (tentativa 1)
SaveResults → FALHA (tentativa 2)
SaveResults → FALHA (tentativa 3)
RollbackStep → SUCESSO (reverte SaveResults)
CompensateTransaction → SUCESSO
Workflow → FALHADO (com compensação)
```



## Exemplo 4: Retomar Workflow de Etapa Específica

### Cenário
Um workflow falhou na etapa EnrichData devido a um bug. O bug foi corrigido e você quer reprocessar apenas a partir dessa etapa.

### Código

```python
from workflow_starter import WorkflowStarter

starter = WorkflowStarter()

# IDs do workflow que falhou
workflow_id = 'workflow-abc-123'
run_id = 'run-xyz-456'

# Retoma a partir da etapa EnrichData
starter.resume_workflow_from_step(
    workflow_id=workflow_id,
    run_id=run_id,
    step_name='EnrichData'
)

print(f"Workflow {workflow_id} será retomado a partir de EnrichData")
```

### Resultado

O workflow:
1. Recebe o sinal RESUME_FROM_STEP
2. Decision Worker detecta o marcador
3. Agenda a atividade EnrichData
4. Continua o fluxo normal: SaveResults → NotifyCompletion

## Exemplo 5: Consultar Histórico de Workflow

### Cenário
Você quer auditar todas as ações que ocorreram em um workflow.

### Código

```python
from workflow_starter import WorkflowStarter
import json

starter = WorkflowStarter()

# Obtém histórico completo
events = starter.get_workflow_history(
    workflow_id='workflow-abc-123',
    run_id='run-xyz-456'
)

# Imprime eventos formatados
for event in events:
    event_type = event['eventType']
    timestamp = event['eventTimestamp']
    
    print(f"\n[{timestamp}] {event_type}")
    
    # Detalhes específicos por tipo de evento
    if event_type == 'WorkflowExecutionStarted':
        attrs = event['workflowExecutionStartedEventAttributes']
        input_data = json.loads(attrs.get('input', '{}'))
        print(f"  Input: {input_data}")
    
    elif event_type == 'ActivityTaskCompleted':
        attrs = event['activityTaskCompletedEventAttributes']
        result = json.loads(attrs.get('result', '{}'))
        print(f"  Result: {result}")
    
    elif event_type == 'ActivityTaskFailed':
        attrs = event['activityTaskFailedEventAttributes']
        reason = attrs.get('reason', 'Unknown')
        print(f"  Reason: {reason}")
```

### Saída Exemplo

```
[2024-01-15 10:30:00] WorkflowExecutionStarted
  Input: {'order_id': 'ORD-123', 'items': [...]}

[2024-01-15 10:30:01] DecisionTaskScheduled

[2024-01-15 10:30:02] DecisionTaskStarted

[2024-01-15 10:30:03] DecisionTaskCompleted

[2024-01-15 10:30:04] ActivityTaskScheduled

[2024-01-15 10:30:05] ActivityTaskStarted

[2024-01-15 10:30:06] ActivityTaskCompleted
  Result: {'status': 'validated', 'order_id': 'ORD-123'}

...
```

## Exemplo 6: Terminar Workflow Manualmente

### Cenário
Um workflow está travado ou precisa ser cancelado por motivos de negócio.

### Código

```python
from workflow_starter import WorkflowStarter

starter = WorkflowStarter()

# Termina o workflow
starter.terminate_workflow(
    workflow_id='workflow-abc-123',
    run_id='run-xyz-456',
    reason='Pedido cancelado pelo cliente'
)

print("Workflow terminado com sucesso")
```

## Exemplo 7: Workflow com Dados Complexos

### Cenário
Processar um pedido com múltiplos itens e cálculos complexos.

### Código

```python
from workflow_starter import WorkflowStarter
from datetime import datetime

starter = WorkflowStarter()

# Dados complexos do pedido
order_data = {
    'order_id': 'ORD-2024-002',
    'created_at': datetime.now().isoformat(),
    'customer': {
        'id': 'CUST-67890',
        'name': 'João Silva',
        'email': 'joao@example.com',
        'tier': 'premium'
    },
    'items': [
        {
            'sku': 'PROD-001',
            'name': 'Notebook',
            'quantity': 1,
            'unit_price': 3500.00,
            'discount': 0.10
        },
        {
            'sku': 'PROD-002',
            'name': 'Mouse',
            'quantity': 2,
            'unit_price': 50.00,
            'discount': 0.05
        }
    ],
    'shipping': {
        'method': 'express',
        'address': {
            'street': 'Rua Exemplo, 123',
            'city': 'São Paulo',
            'state': 'SP',
            'zip': '01234-567'
        },
        'cost': 25.00
    },
    'payment': {
        'method': 'credit_card',
        'installments': 3
    },
    'metadata': {
        'source': 'mobile_app',
        'campaign': 'BLACK_FRIDAY_2024'
    }
}

# Inicia o workflow
result = starter.start_workflow(order_data)

print(f"Pedido complexo iniciado: {result['workflow_id']}")
```

## Exemplo 8: Monitoramento em Tempo Real

### Cenário
Monitorar o progresso de um workflow em tempo real.

### Código

```python
from workflow_starter import WorkflowStarter
import time

def monitor_workflow(workflow_id, run_id, interval=5):
    """
    Monitora um workflow até sua conclusão.
    
    Args:
        workflow_id: ID do workflow
        run_id: ID da execução
        interval: Intervalo de polling em segundos
    """
    starter = WorkflowStarter()
    
    print(f"Monitorando workflow {workflow_id}...")
    print("=" * 60)
    
    last_event_count = 0
    
    while True:
        try:
            # Obtém histórico
            events = starter.get_workflow_history(workflow_id, run_id)
            
            # Mostra apenas novos eventos
            new_events = events[last_event_count:]
            
            for event in new_events:
                event_type = event['eventType']
                timestamp = event['eventTimestamp']
                print(f"[{timestamp}] {event_type}")
                
                # Verifica se workflow terminou
                if event_type in ['WorkflowExecutionCompleted', 
                                 'WorkflowExecutionFailed',
                                 'WorkflowExecutionTerminated']:
                    print("=" * 60)
                    print(f"Workflow finalizado: {event_type}")
                    return
            
            last_event_count = len(events)
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("\nMonitoramento interrompido pelo usuário")
            break
        except Exception as e:
            print(f"Erro ao monitorar: {e}")
            break

# Uso
if __name__ == '__main__':
    monitor_workflow(
        workflow_id='workflow-abc-123',
        run_id='run-xyz-456',
        interval=3
    )
```

## Exemplo 9: Batch Processing

### Cenário
Processar múltiplos pedidos em lote.

### Código

```python
from workflow_starter import WorkflowStarter
import time

def process_batch(orders):
    """
    Processa um lote de pedidos.
    
    Args:
        orders: Lista de dicionários com dados dos pedidos
    
    Returns:
        Lista de workflow IDs iniciados
    """
    starter = WorkflowStarter()
    workflow_ids = []
    
    print(f"Processando lote de {len(orders)} pedidos...")
    
    for i, order in enumerate(orders, 1):
        try:
            result = starter.start_workflow(order)
            workflow_ids.append(result['workflow_id'])
            print(f"[{i}/{len(orders)}] Pedido {order['order_id']} iniciado")
            
            # Pequeno delay para não sobrecarregar
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[{i}/{len(orders)}] Erro ao processar {order['order_id']}: {e}")
    
    print(f"\nTotal processado: {len(workflow_ids)}/{len(orders)}")
    return workflow_ids

# Uso
orders_batch = [
    {'order_id': 'ORD-001', 'items': [...]},
    {'order_id': 'ORD-002', 'items': [...]},
    {'order_id': 'ORD-003', 'items': [...]},
    # ... mais pedidos
]

workflow_ids = process_batch(orders_batch)
print(f"Workflows iniciados: {workflow_ids}")
```

## Exemplo 10: Integração com Sistema Externo

### Cenário
Adicionar uma nova atividade que integra com API externa.

### Código

```python
# Em activity_worker.py, adicione:

import requests

def call_external_api(self, input_data):
    """
    Chama API externa para enriquecer dados.
    
    Args:
        input_data: Dados do workflow
        
    Returns:
        Dados enriquecidos da API externa
    """
    print("Executing: CallExternalAPI")
    
    order_id = input_data.get('order_id')
    
    try:
        # Chama API externa
        response = requests.post(
            'https://api.example.com/enrich',
            json={'order_id': order_id},
            timeout=10
        )
        response.raise_for_status()
        
        external_data = response.json()
        
        return {
            'status': 'api_called',
            'order_id': order_id,
            'external_data': external_data,
            'called_at': time.time()
        }
        
    except requests.RequestException as e:
        # Falha será tratada com retry automático
        raise Exception(f"API call failed: {str(e)}")

# Registre a nova atividade no __init__:
self.activities['CallExternalAPI'] = self.call_external_api
```

## Dicas e Boas Práticas

### 1. Idempotência

Sempre implemente atividades de forma idempotente:

```python
def save_results(self, input_data):
    order_id = input_data.get('order_id')
    
    # Verifica se já foi salvo
    if self.already_saved(order_id):
        print(f"Order {order_id} already saved, skipping")
        return self.get_existing_record(order_id)
    
    # Salva apenas se não existir
    return self.save_new_record(input_data)
```

### 2. Timeouts Apropriados

Configure timeouts baseados no comportamento real:

```python
# Para operações rápidas (< 1 min)
ACTIVITY_TASK_TIMEOUT = '60'

# Para operações longas (5-10 min)
ACTIVITY_TASK_TIMEOUT = '600'
```

### 3. Dados Grandes

Para dados > 32KB, use referências:

```python
# Ruim: Passar dados grandes diretamente
workflow_input = {
    'large_data': [... 100MB de dados ...]
}

# Bom: Passar referência
workflow_input = {
    's3_bucket': 'my-bucket',
    's3_key': 'data/large-file.json'
}
```

### 4. Logging Estruturado

Use logging estruturado para facilitar debugging:

```python
import logging
import json

logger = logging.getLogger(__name__)

def process_data(self, input_data):
    logger.info(
        "Processing data",
        extra={
            'order_id': input_data.get('order_id'),
            'step': 'process_data',
            'timestamp': time.time()
        }
    )
```
