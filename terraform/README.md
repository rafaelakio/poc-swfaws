# Terraform - POC SWF AWS

Configuração Terraform para deploy do AWS Simple Workflow Service (SWF) com Lambda workers.

## 📁 Estrutura

```
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
└── terraform.tfvars.example
```

## 🚀 Deploy

### Recursos Criados

- SWF Domain
- Lambda Functions (Decision Worker e Activity Worker)
- EventBridge Rules (triggers periódicos)
- CloudWatch Log Groups
- SNS Topic para notificações
- IAM Roles e Policies
- CloudWatch Alarms

### Pré-requisitos

Antes de executar o Terraform, você precisa criar os pacotes Lambda:

```bash
# 1. Criar Lambda Layer com dependências
mkdir -p python
pip install boto3 python-dotenv -t python/
zip -r lambda_layer.zip python/
rm -rf python

# 2. Criar pacote do Decision Worker
zip decision_worker.zip decision_worker.py config.py

# 3. Criar pacote do Activity Worker
zip activity_worker.zip activity_worker.py config.py
```

### Deploy

```bash
# Copiar e editar variáveis
cp terraform.tfvars.example terraform.tfvars

# Inicializar Terraform
terraform init

# Planejar mudanças
terraform plan

# Aplicar configuração
terraform apply
```

### Outputs

```bash
# Ver informações do deployment
terraform output

# Outputs disponíveis:
# - swf_domain_name
# - swf_domain_arn
# - decision_worker_function_name
# - activity_worker_function_name
# - sns_topic_arn
```

## 🔧 Como Funciona

1. **SWF Domain**: Registrado com retenção de 30 dias
2. **Lambda Workers**: Executam a cada 1 minuto via EventBridge
3. **Decision Worker**: Orquestra o fluxo do workflow
4. **Activity Worker**: Executa as atividades de negócio
5. **CloudWatch Alarms**: Monitora erros e envia para SNS

## 🎮 Iniciar Workflow

Após o deploy, use o script Python para iniciar workflows:

```python
# workflow_starter.py já está configurado
python workflow_starter.py
```

Ou use o AWS CLI:

```bash
aws swf start-workflow-execution \
  --domain business-process-domain \
  --workflow-id workflow-$(date +%s) \
  --workflow-type name=BusinessProcessWorkflow,version=1.0 \
  --task-list name=business-process-tasks \
  --input '{"order_id":"ORD-123","items":["item1","item2"]}'
```

## 📊 Monitoramento

### CloudWatch Logs

```bash
# Ver logs do Decision Worker
aws logs tail /aws/lambda/poc-swfaws-decision-worker --follow

# Ver logs do Activity Worker
aws logs tail /aws/lambda/poc-swfaws-activity-worker --follow
```

### Console AWS SWF

Acesse o console AWS SWF para visualizar:
- Execuções ativas
- Histórico de eventos
- Workflows completados/falhados

## 🔧 Configuração

### Variáveis Importantes

- `swf_domain_name`: Nome do domínio SWF
- `swf_task_list`: Nome da task list
- `retention_days`: Dias de retenção do histórico (padrão: 30)

### Ajustar Frequência dos Workers

Edite em `main.tf`:

```hcl
schedule_expression = "rate(1 minute)"  # Altere conforme necessário
```

## 🗑️ Destruir Recursos

```bash
terraform destroy
```

**Nota:** O SWF Domain não pode ser deletado se houver execuções ativas. Aguarde todas as execuções terminarem.

## 💰 Custos Estimados

- SWF: $0.00012 por workflow execution
- Lambda: Primeira 1M de requests grátis
- CloudWatch Logs: ~$0.50/GB
- Total: ~$5-10/mês (uso moderado)

## 📝 Notas

- Os workers são executados periodicamente (1 minuto)
- Workflows podem levar alguns minutos para iniciar
- Configure o SNS topic para receber notificações de erros
- Use CloudWatch Insights para análise de logs
