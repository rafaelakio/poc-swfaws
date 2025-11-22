# Arquitetura da Aplicação AWS SWF

## Visão Geral

Esta aplicação implementa um workflow distribuído usando AWS Simple Workflow Service (SWF) com arquitetura baseada em workers.

## Componentes Principais

### 1. AWS SWF Service (Gerenciado pela AWS)

O SWF atua como o orquestrador central:
- Mantém o estado do workflow
- Armazena histórico de eventos
- Distribui tarefas para workers
- Garante entrega de tarefas (at-least-once)

### 2. Decision Worker

**Responsabilidade**: Lógica de orquestração

```
┌─────────────────────────────────┐
│     Decision Worker             │
│                                 │
│  ┌──────────────────────────┐  │
│  │  Poll for Decision Task  │  │
│  └───────────┬──────────────┘  │
│              │                  │
│              ▼                  │
│  ┌──────────────────────────┐  │
│  │   Analyze Event History  │  │
│  └───────────┬──────────────┘  │
│              │                  │
│              ▼                  │
│  ┌──────────────────────────┐  │
│  │    Make Decisions        │  │
│  │  - Schedule Activities   │  │
│  │  - Handle Retries        │  │
│  │  - Manage Rollbacks      │  │
│  └───────────┬──────────────┘  │
│              │                  │
│              ▼                  │
│  ┌──────────────────────────┐  │
│  │  Respond to SWF          │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
```

### 3. Activity Worker

**Responsabilidade**: Execução de atividades de negócio

```
┌─────────────────────────────────┐
│     Activity Worker             │
│                                 │
│  ┌──────────────────────────┐  │
│  │  Poll for Activity Task  │  │
│  └───────────┬──────────────┘  │
│              │                  │
│              ▼                  │
│  ┌──────────────────────────┐  │
│  │   Execute Business       │  │
│  │   Logic                  │  │
│  └───────────┬──────────────┘  │
│              │                  │
│              ▼                  │
│  ┌──────────────────────────┐  │
│  │  Report Result to SWF    │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
```



### 4. Workflow Starter

**Responsabilidade**: Controle de execuções

- Inicia novos workflows
- Envia sinais para workflows em execução
- Consulta histórico e status
- Termina workflows quando necessário

## Fluxo de Dados

### Início de Workflow

```
Workflow Starter
    │
    │ start_workflow_execution()
    ▼
AWS SWF
    │
    │ Creates Decision Task
    ▼
Decision Worker
    │
    │ Analyzes: WorkflowExecutionStarted
    │ Decision: Schedule first activity
    ▼
AWS SWF
    │
    │ Creates Activity Task
    ▼
Activity Worker
    │
    │ Executes: ValidateInput
    │ Reports: Success
    ▼
AWS SWF
    │
    │ Creates Decision Task
    ▼
Decision Worker
    │
    │ Analyzes: ActivityTaskCompleted
    │ Decision: Schedule next activity
    ▼
... (continua até conclusão)
```

## Padrões Implementados

### 1. Retry Pattern

Implementa retry automático com limite de tentativas:

```python
if retry_count < 3:
    # Tenta novamente
    schedule_activity(failed_activity)
else:
    # Inicia rollback
    initiate_rollback()
```

### 2. SAGA Pattern

Implementa transações distribuídas com compensação:

```
Normal Flow:
  Step 1 → Step 2 → Step 3 → Complete

Failure Flow:
  Step 1 → Step 2 → [FAIL] → Rollback Step 2 → Compensate → Fail Workflow
```

### 3. State Machine Pattern

O Decision Worker implementa uma máquina de estados:

```
States:
- RUNNING: Executando atividades normalmente
- RETRYING: Tentando novamente após falha
- ROLLING_BACK: Revertendo mudanças
- COMPENSATING: Executando compensação
- COMPLETED: Workflow concluído
- FAILED: Workflow falhou
```

## Garantias e Características

### Durabilidade

- Todo estado é persistido no SWF
- Histórico completo de eventos mantido por 30 dias
- Workers podem falhar sem perder estado

### Escalabilidade

- Múltiplos workers podem rodar em paralelo
- SWF distribui tarefas automaticamente
- Horizontal scaling de workers

### Confiabilidade

- At-least-once delivery de tarefas
- Timeouts configuráveis em múltiplos níveis
- Heartbeats para detectar workers travados

## Segurança

### Autenticação

- Credenciais AWS via IAM
- Suporte a roles e temporary credentials
- Princípio do menor privilégio

### Permissões Necessárias

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "swf:RegisterDomain",
        "swf:RegisterWorkflowType",
        "swf:RegisterActivityType",
        "swf:StartWorkflowExecution",
        "swf:PollForDecisionTask",
        "swf:PollForActivityTask",
        "swf:RespondDecisionTaskCompleted",
        "swf:RespondActivityTaskCompleted",
        "swf:RespondActivityTaskFailed",
        "swf:GetWorkflowExecutionHistory",
        "swf:SignalWorkflowExecution",
        "swf:TerminateWorkflowExecution"
      ],
      "Resource": "*"
    }
  ]
}
```

## Monitoramento

### Métricas Importantes

- Taxa de sucesso de atividades
- Tempo médio de execução
- Número de retries
- Taxa de rollbacks
- Workflows ativos

### Logs

Cada componente gera logs estruturados:
- Decision Worker: Decisões tomadas
- Activity Worker: Atividades executadas
- Workflow Starter: Workflows iniciados

## Limitações e Considerações

### Limitações do SWF

- Máximo 25.000 eventos por workflow
- Payload máximo de 32KB por evento
- Taxa de 200 TPS por domínio

### Considerações de Design

- Workers devem ser idempotentes
- Atividades devem ter timeout apropriado
- Dados grandes devem ser armazenados externamente (S3)

## Extensibilidade

### Adicionando Novas Atividades

1. Adicione método em `ActivityWorker`
2. Registre no mapeamento `self.activities`
3. Execute `setup.py` para registrar no SWF
4. Adicione na sequência em `DecisionWorker.make_decisions()`

### Customizando Lógica de Decisão

Modifique `DecisionWorker.make_decisions()` para:
- Adicionar condições especiais
- Implementar branches paralelos
- Adicionar timers
- Implementar workflows filhos
