# Perguntas Frequentes (FAQ)

## Geral

### O que é AWS SWF?

AWS Simple Workflow Service (SWF) é um serviço gerenciado que facilita a coordenação de trabalho entre componentes distribuídos de aplicações. Ele mantém o estado da execução e garante que tarefas sejam executadas de forma confiável.

### Por que usar SWF ao invés de Step Functions?

- **SWF**: Mais controle, código customizado, ideal para workflows complexos com lógica de decisão sofisticada
- **Step Functions**: Mais simples, baseado em JSON, ideal para workflows mais diretos

### Esta aplicação é production-ready?

Este é um exemplo educacional. Para produção, adicione:
- Testes automatizados
- Monitoramento e alertas
- Tratamento de erros mais robusto
- Logging estruturado
- Métricas de performance

## Instalação e Configuração

### Erro: "ModuleNotFoundError: No module named 'boto3'"

**Solução**: Instale as dependências

```bash
pip install -r requirements.txt
```

### Erro: "Unable to locate credentials"

**Solução**: Configure suas credenciais AWS no arquivo `.env`

```env
AWS_ACCESS_KEY_ID=sua_key
AWS_SECRET_ACCESS_KEY=sua_secret
AWS_REGION=us-east-1
```

### Como obter credenciais AWS?

1. Acesse o Console AWS
2. Vá para IAM → Users
3. Crie um novo usuário ou selecione existente
4. Gere Access Keys
5. Copie para o arquivo `.env`

### Quais permissões IAM são necessárias?

Permissões mínimas para SWF:
- `swf:RegisterDomain`
- `swf:RegisterWorkflowType`
- `swf:RegisterActivityType`
- `swf:StartWorkflowExecution`
- `swf:PollForDecisionTask`
- `swf:PollForActivityTask`
- `swf:RespondDecisionTaskCompleted`
- `swf:RespondActivityTaskCompleted`
- `swf:RespondActivityTaskFailed`
- `swf:GetWorkflowExecutionHistory`

## Execução

### Workers não recebem tarefas

**Possíveis causas**:

1. **Domínio não registrado**
   ```bash
   python setup.py
   ```

2. **Task list incorreta**
   - Verifique `SWF_TASK_LIST` no `.env`
   - Deve ser igual em todos os componentes

3. **Workflow não iniciado**
   ```bash
   python workflow_starter.py
   ```

### Como executar múltiplos workers?

Abra múltiplos terminais:

```bash
# Terminal 1
python decision_worker.py

# Terminal 2
python decision_worker.py

# Terminal 3
python activity_worker.py

# Terminal 4
python activity_worker.py
```

SWF distribui tarefas automaticamente entre workers.

### Posso rodar workers em máquinas diferentes?

Sim! Desde que:
- Tenham acesso à AWS
- Usem as mesmas credenciais
- Configurem o mesmo domínio e task list

### Como parar os workers?

Pressione `Ctrl+C` no terminal. Os workers param gracefully.

## Workflow

### Como adicionar uma nova atividade?

1. **Adicione o método em `activity_worker.py`**:

```python
def minha_nova_atividade(self, input_data):
    print("Executing: MinhaNovaAtividade")
    # Sua lógica aqui
    return {'status': 'completed'}
```

2. **Registre no mapeamento**:

```python
self.activities['MinhaNovaAtividade'] = self.minha_nova_atividade
```

3. **Execute setup**:

```bash
python setup.py
```

4. **Adicione na sequência em `decision_worker.py`**:

```python
workflow_steps = [
    'ValidateInput',
    'ProcessData',
    'MinhaNovaAtividade',  # Nova atividade
    'EnrichData',
    'SaveResults',
    'NotifyCompletion'
]
```

### Como alterar o número de retries?

Em `decision_worker.py`, altere:

```python
if retry_count < 3:  # Altere este número
    # Retry
```

### Como aumentar o timeout de uma atividade?

Em `config.py`, altere:

```python
ACTIVITY_START_TO_CLOSE_TIMEOUT = '600'  # 10 minutos
```

Depois execute `setup.py` novamente.

### Workflow está demorando muito

**Possíveis causas**:

1. **Atividades lentas**: Otimize a lógica de negócio
2. **Poucos workers**: Execute mais instâncias
3. **Timeouts muito longos**: Reduza timeouts
4. **Retries excessivos**: Reduza número de retries

### Como debugar um workflow?

1. **Consulte o histórico**:

```python
events = starter.get_workflow_history(workflow_id, run_id)
for event in events:
    print(event)
```

2. **Verifique logs dos workers**:
   - Decision Worker mostra decisões tomadas
   - Activity Worker mostra atividades executadas

3. **Use o Console AWS**:
   - Acesse SWF no console
   - Visualize execuções e eventos

## Erros Comuns

### "WorkflowType not registered"

**Solução**: Execute o setup

```bash
python setup.py
```

### "ActivityType not registered"

**Solução**: Execute o setup

```bash
python setup.py
```

### "Workflow execution already started"

**Causa**: Tentou iniciar workflow com mesmo ID

**Solução**: Cada execução precisa de ID único (já implementado com UUID)

### "Task token has expired"

**Causa**: Worker demorou muito para responder

**Solução**: 
- Aumente timeouts em `config.py`
- Otimize lógica das atividades
- Implemente heartbeats para atividades longas

### Atividade sempre falha com timeout

**Solução**:

1. **Aumente timeout**:
```python
ACTIVITY_START_TO_CLOSE_TIMEOUT = '900'  # 15 minutos
```

2. **Adicione heartbeat**:
```python
def long_running_activity(self, input_data):
    for i in range(10):
        # Trabalho
        time.sleep(30)
        # Envia heartbeat
        self.swf_client.client.record_activity_task_heartbeat(
            taskToken=task_token
        )
```

## Rollback e Compensação

### Quando o rollback é acionado?

Após 3 falhas consecutivas da mesma atividade.

### Como customizar a lógica de rollback?

Modifique o método `rollback_step` em `activity_worker.py`:

```python
def rollback_step(self, input_data):
    step = input_data.get('step_to_rollback')
    
    if step == 'SaveResults':
        # Deleta registros salvos
        self.delete_saved_records(input_data)
    elif step == 'ProcessData':
        # Reverte processamento
        self.revert_processing(input_data)
    
    return {'status': 'rolled_back', 'step': step}
```

### O que é compensação?

Compensação é uma transação que desfaz os efeitos de uma transação anterior quando rollback direto não é possível. Exemplo: estornar um pagamento já processado.

## Retomada de Etapas

### Como retomar um workflow pausado?

```python
starter.resume_workflow_from_step(
    workflow_id='workflow-id',
    run_id='run-id',
    step_name='ProcessData'
)
```

### Posso retomar de qualquer etapa?

Sim, desde que a etapa esteja definida em `workflow_steps`.

### O que acontece com dados de etapas anteriores?

São preservados e passados para a etapa retomada via `previous_results`.

## Performance

### Quantos workflows posso executar simultaneamente?

Limitado por:
- Número de workers rodando
- Limites da conta AWS (200 TPS por domínio)
- Recursos da máquina

### Como escalar horizontalmente?

Execute mais instâncias de workers em diferentes máquinas:

```bash
# Máquina 1
python decision_worker.py
python activity_worker.py

# Máquina 2
python decision_worker.py
python activity_worker.py

# Máquina 3
python activity_worker.py
python activity_worker.py
```

### Qual o custo do AWS SWF?

Preços (podem variar por região):
- $0.00001 por workflow execution
- $0.00001 por activity task
- $0.00001 por decision task

Exemplo: 1000 workflows com 5 atividades cada = ~$0.06

## Monitoramento

### Como monitorar workflows em produção?

1. **CloudWatch Metrics**:
   - Workflows iniciados
   - Atividades completadas/falhadas
   - Tempo de execução

2. **Logs Estruturados**:
```python
import logging
logger = logging.getLogger(__name__)
logger.info('Activity completed', extra={'order_id': order_id})
```

3. **Dashboard Custom**:
   - Consulte histórico via API
   - Agregue métricas
   - Visualize em dashboard

### Como receber alertas de falhas?

1. **CloudWatch Alarms**:
   - Configure alarmes para métricas
   - Envie para SNS
   - SNS notifica via email/SMS

2. **Custom Monitoring**:
```python
def monitor_failures():
    events = get_workflow_history(workflow_id, run_id)
    failures = [e for e in events if 'Failed' in e['eventType']]
    if len(failures) > 3:
        send_alert('Multiple failures detected')
```

## Segurança

### Como proteger credenciais AWS?

1. **Nunca commite `.env`** (já no `.gitignore`)
2. **Use IAM Roles** quando possível
3. **Rotacione credenciais** regularmente
4. **Use AWS Secrets Manager** em produção

### Dados sensíveis no workflow?

**Não passe dados sensíveis diretamente**:

```python
# Ruim
workflow_input = {'credit_card': '1234-5678-9012-3456'}

# Bom
workflow_input = {'payment_token': 'tok_abc123'}
```

### Como auditar execuções?

Todo histórico é mantido no SWF por 30 dias:

```python
events = starter.get_workflow_history(workflow_id, run_id)
# Analise eventos para auditoria
```

## Troubleshooting Avançado

### Worker trava sem erros

**Possíveis causas**:
1. Deadlock na lógica de negócio
2. Operação bloqueante (I/O)
3. Timeout muito longo

**Solução**: Adicione logging detalhado e timeouts

### Memória crescendo continuamente

**Causa**: Possível memory leak

**Solução**:
1. Revise código para referências circulares
2. Use profiler: `python -m memory_profiler activity_worker.py`
3. Reinicie workers periodicamente

### Como testar localmente sem AWS?

Use mocks:

```python
from unittest.mock import Mock, patch

@patch('boto3.client')
def test_activity(mock_client):
    worker = ActivityWorker()
    result = worker.validate_input({'order_id': 'TEST-001'})
    assert result['status'] == 'validated'
```

## Migração e Deployment

### Como migrar para produção?

1. **Separe ambientes**:
```env
# .env.prod
SWF_DOMAIN=production-domain
SWF_TASK_LIST=production-tasks
```

2. **Use CI/CD**:
```yaml
# .github/workflows/deploy.yml
- name: Deploy workers
  run: |
    python setup.py
    supervisorctl restart swf-workers
```

3. **Containerize**:
```dockerfile
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "activity_worker.py"]
```

### Como fazer rollback de código?

1. Workers antigos continuam funcionando
2. Deploy nova versão com nova `WORKFLOW_VERSION`
3. Workflows novos usam nova versão
4. Workflows antigos completam com versão antiga
