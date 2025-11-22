# Diagramas e Fluxos Visuais

## Arquitetura Geral

```
┌─────────────────────────────────────────────────────────────┐
│                     AWS Cloud                                │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           AWS Simple Workflow Service              │    │
│  │                                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐              │    │
│  │  │   Domain     │  │  Task Lists  │              │    │
│  │  │              │  │              │              │    │
│  │  │ - Workflows  │  │ - Decision   │              │    │
│  │  │ - Activities │  │ - Activity   │              │    │
│  │  └──────────────┘  └──────────────┘              │    │
│  │                                                     │    │
│  │  ┌──────────────────────────────────────────┐    │    │
│  │  │      Event History Storage               │    │    │
│  │  │  (Mantém estado e histórico completo)    │    │    │
│  │  └──────────────────────────────────────────┘    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                          ▲  ▲  ▲
                          │  │  │
        ┌─────────────────┘  │  └─────────────────┐
        │                    │                     │
        │                    │                     │
┌───────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐
│   Workflow     │  │    Decision     │  │    Activity     │
│   Starter      │  │    Worker       │  │    Worker       │
│                │  │                 │  │                 │
│ - Start        │  │ - Poll Tasks    │  │ - Poll Tasks    │
│ - Signal       │  │ - Analyze       │  │ - Execute       │
│ - Monitor      │  │ - Decide        │  │ - Report        │
└────────────────┘  └─────────────────┘  └─────────────────┘
```

## Fluxo de Execução Normal

```
Início
  │
  ▼
┌─────────────────┐
│ Start Workflow  │ ← Workflow Starter
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Decision Task   │ ← SWF cria decision task
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ValidateInput   │ ← Decision Worker agenda
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Execute         │ ← Activity Worker executa
│ ValidateInput   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Decision Task   │ ← SWF cria nova decision task
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ProcessData     │ ← Decision Worker agenda próxima
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Execute         │ ← Activity Worker executa
│ ProcessData     │
└────────┬────────┘
         │
         ▼
       ...
         │
         ▼
┌─────────────────┐
│ Complete        │ ← Decision Worker completa workflow
│ Workflow        │
└─────────────────┘
```



## Fluxo com Retry e Rollback

```
Início
  │
  ▼
ValidateInput ✓
  │
  ▼
ProcessData ✓
  │
  ▼
EnrichData ✗ (Falha 1)
  │
  ▼
EnrichData ✗ (Falha 2)
  │
  ▼
EnrichData ✗ (Falha 3)
  │
  ▼
┌─────────────────────┐
│ Max Retries Reached │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Record Marker:      │
│ ROLLBACK_INITIATED  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ RollbackStep        │
│ (EnrichData)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Compensate          │
│ Transaction         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Fail Workflow       │
│ (with compensation) │
└─────────────────────┘
```

## Fluxo de Retomada de Etapa

```
Workflow Pausado/Falhado
  │
  │ (Correção manual do problema)
  │
  ▼
┌─────────────────────┐
│ Send Signal:        │
│ RESUME_FROM_STEP    │
│ step: "ProcessData" │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Decision Task       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Detect Marker:      │
│ RESUME_FROM_STEP    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Schedule Activity:  │
│ ProcessData         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Continue Normal     │
│ Execution           │
└─────────────────────┘
```

## Estados do Workflow

```
┌─────────┐
│ STARTED │
└────┬────┘
     │
     ▼
┌─────────┐     ┌──────────┐
│ RUNNING │────▶│ RETRYING │
└────┬────┘     └────┬─────┘
     │               │
     │               ▼
     │          ┌──────────────┐
     │          │ ROLLING_BACK │
     │          └────┬─────────┘
     │               │
     │               ▼
     │          ┌──────────────┐
     │          │ COMPENSATING │
     │          └────┬─────────┘
     │               │
     ▼               ▼
┌───────────┐   ┌────────┐
│ COMPLETED │   │ FAILED │
└───────────┘   └────────┘
```

## Ciclo de Vida de uma Atividade

```
┌──────────────┐
│  SCHEDULED   │ ← Decision Worker agenda
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   STARTED    │ ← Activity Worker pega tarefa
└──────┬───────┘
       │
       ├─────────────┐
       │             │
       ▼             ▼
┌──────────────┐  ┌──────────────┐
│  COMPLETED   │  │    FAILED    │
└──────────────┘  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Retry < 3?   │
                  └──────┬───────┘
                         │
                    ┌────┴────┐
                    │         │
                   Sim       Não
                    │         │
                    ▼         ▼
              ┌──────────┐  ┌──────────┐
              │ SCHEDULE │  │ ROLLBACK │
              │  AGAIN   │  │ PROCESS  │
              └──────────┘  └──────────┘
```

## Interação entre Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    Linha do Tempo                            │
└─────────────────────────────────────────────────────────────┘

Workflow Starter    Decision Worker    Activity Worker    SWF
      │                    │                  │            │
      │ StartWorkflow      │                  │            │
      ├───────────────────────────────────────────────────▶│
      │                    │                  │            │
      │                    │ PollDecisionTask │            │
      │                    │◀─────────────────────────────┤
      │                    │                  │            │
      │                    │ ScheduleActivity │            │
      │                    ├─────────────────────────────▶│
      │                    │                  │            │
      │                    │                  │ PollActivity│
      │                    │                  │◀───────────┤
      │                    │                  │            │
      │                    │                  │ Execute    │
      │                    │                  │            │
      │                    │                  │ Complete   │
      │                    │                  ├───────────▶│
      │                    │                  │            │
      │                    │ PollDecisionTask │            │
      │                    │◀─────────────────────────────┤
      │                    │                  │            │
      │                    │ CompleteWorkflow │            │
      │                    ├─────────────────────────────▶│
      │                    │                  │            │
```

## Estrutura de Dados

```
Workflow Input
├── order_id: string
├── customer_id: string
├── items: array
│   ├── sku: string
│   ├── quantity: number
│   └── price: number
└── metadata: object

Activity Result
├── status: string
├── order_id: string
├── processed_at: timestamp
└── data: object
    └── (dados específicos da atividade)

Event History
├── eventId: number
├── eventType: string
├── eventTimestamp: datetime
└── attributes: object
    └── (atributos específicos do evento)
```

## Padrão de Comunicação

```
┌──────────────────────────────────────────────────────┐
│              Long Polling Pattern                     │
└──────────────────────────────────────────────────────┘

Worker                                    SWF
  │                                        │
  │ PollForTask (timeout: 60s)            │
  ├──────────────────────────────────────▶│
  │                                        │
  │         (aguarda até 60s)              │
  │                                        │
  │◀──────────────────────────────────────┤
  │         Task ou Empty Response         │
  │                                        │
  │ Process Task                           │
  │                                        │
  │ Respond                                │
  ├──────────────────────────────────────▶│
  │                                        │
  │ PollForTask (timeout: 60s)            │
  ├──────────────────────────────────────▶│
  │                                        │
  │         (loop contínuo)                │
```

## Fluxo de Decisão Detalhado

```
┌─────────────────────────────────────────────────────┐
│         Decision Worker - Make Decisions            │
└─────────────────────────────────────────────────────┘

Receive Decision Task
        │
        ▼
Analyze Event History
        │
        ├─────────────────┬─────────────────┬──────────────┐
        │                 │                 │              │
        ▼                 ▼                 ▼              ▼
Has Failed         Has Marker        All Steps      Normal
Activities?        RESUME?           Complete?      Flow?
        │                 │                 │              │
       Yes               Yes               Yes            Yes
        │                 │                 │              │
        ▼                 ▼                 ▼              ▼
Retry < 3?         Resume from        Complete       Schedule
        │          Specific Step      Workflow       Next Step
   ┌────┴────┐            │                 │              │
  Yes       No            │                 │              │
   │         │            │                 │              │
   ▼         ▼            │                 │              │
Retry    Rollback         │                 │              │
Activity  Process         │                 │              │
   │         │            │                 │              │
   └─────────┴────────────┴─────────────────┴──────────────┘
                          │
                          ▼
                  Return Decisions
```
