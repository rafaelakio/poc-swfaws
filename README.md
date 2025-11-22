# AWS SWF Workflow - Aplicação de Processos de Negócio

Aplicação completa utilizando AWS Simple Workflow Service (SWF) para executar processos de negócio com capacidades bidirecionais, reprocessamento e retomada de etapas.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Recursos Principais](#recursos-principais)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Execução](#execução)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Fluxo de Trabalho](#fluxo-de-trabalho)
- [Troubleshooting](#troubleshooting)

## 📚 Documentação Completa

- **[INDEX.md](INDEX.md)** - Índice de toda documentação
- **[QUICKSTART.md](QUICKSTART.md)** - Guia de início rápido (5 minutos)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitetura detalhada do sistema
- **[DIAGRAMS.md](DIAGRAMS.md)** - Diagramas e fluxos visuais
- **[EXAMPLES.md](EXAMPLES.md)** - 10+ exemplos práticos de uso
- **[FAQ.md](FAQ.md)** - Perguntas frequentes e soluções
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guia para contribuidores

## 🎯 Visão Geral

Esta aplicação implementa um workflow completo usando AWS SWF com as seguintes capacidades:

- **Execução Bidirecional**: Fluxo pode avançar e retroceder conforme necessário
- **Reprocessamento**: Cada etapa pode ser reprocessada automaticamente em caso de falha
- **Retry Automático**: Até 3 tentativas automáticas por atividade
- **Rollback e Compensação**: Implementa padrão SAGA para transações distribuídas
- **Retomada de Etapas**: Permite retomar o workflow a partir de qualquer etapa
- **Auditoria Completa**: Todo histórico de execução é mantido no SWF

## 🏗️ Arquitetura

A aplicação é composta por três componentes principais:

```
┌─────────────────┐
│  Workflow       │  Inicia workflows e envia sinais
│  Starter        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AWS SWF       │  Orquestra e mantém estado
│   Service       │
└────┬───────┬────┘
     │       │
     ▼       ▼
┌─────────┐ ┌──────────┐
│Decision │ │Activity  │  Executam lógica
│Worker   │ │Worker    │  de negócio
└─────────┘ └──────────┘
```

### Componentes

1. **SWF Client** (`swf_client.py`)
   - Gerencia conexão com AWS SWF
   - Registra domínios e tipos de workflow

2. **Decision Worker** (`decision_worker.py`)
   - Orquestra o fluxo do workflow
   - Toma decisões sobre próximas ações
   - Gerencia retries, rollbacks e retomadas

3. **Activity Worker** (`activity_worker.py`)
   - Executa atividades de negócio
   - Reporta sucesso ou falha

4. **Workflow Starter** (`workflow_starter.py`)
   - Inicia novas execuções
   - Envia sinais para workflows
   - Consulta histórico

## ✨ Recursos Principais

### 1. Retry Automático
- Até 3 tentativas automáticas por atividade
- Backoff exponencial entre tentativas
- Após 3 falhas, inicia processo de rollback

### 2. Rollback e Compensação (Padrão SAGA)
- Rollback automático após falhas persistentes
- Compensação de transações distribuídas
- Mantém consistência eventual

### 3. Retomada de Etapas
- Retome o workflow de qualquer etapa
- Útil para reprocessamento após correções
- Preserva dados de etapas anteriores

### 4. Fluxo Bidirecional
- Avance para próxima etapa
- Retorne para etapas anteriores
- Reprocesse etapas específicas

## 📦 Pré-requisitos

- Python 3.8 ou superior
- Conta AWS com acesso ao SWF
- Credenciais AWS configuradas

## 🚀 Instalação

### 1. Clone o repositório

```bash
cd poc-swfaws
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
```

### 3. Ative o ambiente virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

## ⚙️ Configuração

### 1. Configure as credenciais AWS

Crie um arquivo `.env` na raiz do projeto:

```bash
copy .env.example .env
```

### 2. Edite o arquivo `.env`

```env
AWS_ACCESS_KEY_ID=sua_access_key_aqui
AWS_SECRET_ACCESS_KEY=sua_secret_key_aqui
AWS_REGION=us-east-1
SWF_DOMAIN=business-process-domain
SWF_TASK_LIST=business-process-tasks
```

### 3. Registre o domínio e workflow

```bash
python setup.py
```

## 🎮 Execução

### Opção 1: Script de Automação (Recomendado)

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

O script oferece um menu interativo para:
- Executar setup inicial
- Iniciar workers
- Executar demonstração
- Executar workflows customizados

### Opção 2: Execução Manual

A aplicação requer que três componentes estejam rodando simultaneamente.

**Terminal 1: Decision Worker**
```bash
python decision_worker.py
```

**Terminal 2: Activity Worker**
```bash
python activity_worker.py
```

**Terminal 3: Iniciar Workflow**
```bash
python workflow_starter.py
# ou
python demo.py
```

## 📖 Uso

### Iniciar um Workflow

```python
from workflow_starter import WorkflowStarter

starter = WorkflowStarter()

# Dados de entrada
workflow_input = {
    'order_id': 'ORD-12345',
    'items': ['item1', 'item2', 'item3'],
    'customer_id': 'CUST-789'
}

# Inicia o workflow
result = starter.start_workflow(workflow_input)
print(f"Workflow ID: {result['workflow_id']}")
print(f"Run ID: {result['run_id']}")
```

### Retomar de uma Etapa Específica

```python
# Retoma a partir da etapa ProcessData
starter.resume_workflow_from_step(
    workflow_id='workflow-abc-123',
    run_id='run-xyz-456',
    step_name='ProcessData'
)
```

### Consultar Histórico

```python
# Obtém histórico completo
events = starter.get_workflow_history(
    workflow_id='workflow-abc-123',
    run_id='run-xyz-456'
)

for event in events:
    print(f"{event['eventType']}: {event['eventTimestamp']}")
```

### Terminar um Workflow

```python
starter.terminate_workflow(
    workflow_id='workflow-abc-123',
    run_id='run-xyz-456',
    reason='Cancelamento manual'
)
```

## 📁 Estrutura do Projeto

```
poc-swfaws/
│
├── config.py                 # Configurações centralizadas
├── swf_client.py            # Cliente AWS SWF
├── decision_worker.py       # Orquestrador do workflow
├── activity_worker.py       # Executor de atividades
├── workflow_starter.py      # Iniciador de workflows
├── setup.py                 # Script de configuração inicial
│
├── requirements.txt         # Dependências Python
├── .env.example            # Exemplo de configuração
├── .gitignore              # Arquivos ignorados pelo Git
└── README.md               # Esta documentação
```

## 🔄 Fluxo de Trabalho

### Fluxo Normal

1. **ValidateInput**: Valida dados de entrada
2. **ProcessData**: Processa dados principais
3. **EnrichData**: Enriquece com informações adicionais
4. **SaveResults**: Persiste resultados
5. **NotifyCompletion**: Notifica conclusão

### Fluxo com Falha

1. Atividade falha
2. Retry automático (até 3x)
3. Se continuar falhando:
   - Registra marcador de rollback
   - Executa RollbackStep
   - Executa CompensateTransaction
   - Falha o workflow com compensação

### Fluxo de Retomada

1. Workflow pausado ou falhado
2. Correção manual do problema
3. Envio de sinal RESUME_FROM_STEP
4. Workflow retoma da etapa especificada
5. Continua execução normal

## 🔧 Troubleshooting

### Workers não recebem tarefas

**Problema**: Workers ficam em loop sem receber tarefas.

**Solução**:
- Verifique se o domínio e workflow estão registrados
- Confirme que a task list está correta
- Verifique credenciais AWS

```bash
python setup.py
```

### Erro de credenciais AWS

**Problema**: `UnauthorizedOperation` ou `InvalidClientTokenId`

**Solução**:
- Verifique o arquivo `.env`
- Confirme que as credenciais têm permissões SWF
- Teste com AWS CLI: `aws swf list-domains --registration-status REGISTERED`

### Workflow não inicia

**Problema**: Erro ao iniciar workflow

**Solução**:
- Verifique se o tipo de workflow está registrado
- Confirme que os workers estão rodando
- Verifique logs dos workers

### Atividade sempre falha

**Problema**: Atividade falha mesmo após retries

**Solução**:
- Verifique logs do Activity Worker
- Confirme formato dos dados de entrada
- Adicione tratamento de erro específico na atividade

## 📊 Monitoramento

### Console AWS

Acesse o console AWS SWF para visualizar:
- Execuções ativas
- Histórico de eventos
- Métricas de performance

### Logs Locais

Os workers imprimem logs detalhados:
- Tarefas recebidas
- Atividades executadas
- Decisões tomadas
- Erros e exceções

## 🤝 Contribuindo

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é fornecido como exemplo educacional.

## 🆘 Suporte

Para questões e suporte:
- Abra uma issue no repositório
- Consulte a documentação AWS SWF
- Revise os logs dos workers

## 🔗 Recursos Adicionais

- [Documentação AWS SWF](https://docs.aws.amazon.com/swf/)
- [Boto3 SWF Reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/swf.html)
- [Padrão SAGA](https://microservices.io/patterns/data/saga.html)
