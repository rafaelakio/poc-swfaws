# Guia de Início Rápido

## 5 Minutos para seu Primeiro Workflow

### Passo 1: Instale as Dependências (1 min)

```bash
cd poc-swfaws
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Passo 2: Configure Credenciais (1 min)

Crie arquivo `.env`:

```env
AWS_ACCESS_KEY_ID=sua_key_aqui
AWS_SECRET_ACCESS_KEY=sua_secret_aqui
AWS_REGION=us-east-1
SWF_DOMAIN=business-process-domain
SWF_TASK_LIST=business-process-tasks
```

### Passo 3: Execute Setup (30 seg)

```bash
python setup.py
```

### Passo 4: Inicie os Workers (1 min)

**Terminal 1 - Decision Worker:**
```bash
python decision_worker.py
```

**Terminal 2 - Activity Worker:**
```bash
python activity_worker.py
```

### Passo 5: Execute um Workflow (30 seg)

**Terminal 3:**
```bash
python workflow_starter.py
```

Pronto! Seu primeiro workflow está rodando.

## Próximos Passos

- Leia o [README.md](README.md) completo
- Explore [EXAMPLES.md](EXAMPLES.md) para casos de uso
- Consulte [FAQ.md](FAQ.md) para dúvidas comuns
- Veja [ARCHITECTURE.md](ARCHITECTURE.md) para entender a arquitetura

## Comandos Úteis

```bash
# Ver histórico de um workflow
python -c "from workflow_starter import WorkflowStarter; \
  s = WorkflowStarter(); \
  print(s.get_workflow_history('workflow-id', 'run-id'))"

# Retomar de uma etapa
python -c "from workflow_starter import WorkflowStarter; \
  s = WorkflowStarter(); \
  s.resume_workflow_from_step('workflow-id', 'run-id', 'ProcessData')"
```
