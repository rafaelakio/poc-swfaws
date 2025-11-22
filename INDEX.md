# Índice da Documentação

Bem-vindo à documentação completa da aplicação AWS SWF para processos de negócio!

## 📚 Documentação Disponível

### 🚀 Para Começar

1. **[QUICKSTART.md](QUICKSTART.md)** - Comece aqui!
   - Guia de 5 minutos para executar seu primeiro workflow
   - Comandos essenciais
   - Configuração rápida

2. **[README.md](README.md)** - Documentação Principal
   - Visão geral completa do projeto
   - Instalação detalhada
   - Configuração passo a passo
   - Estrutura do projeto
   - Troubleshooting

### 📖 Aprendizado

3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitetura do Sistema
   - Componentes principais
   - Fluxo de dados
   - Padrões implementados (Retry, SAGA, State Machine)
   - Garantias e características
   - Segurança e permissões

4. **[DIAGRAMS.md](DIAGRAMS.md)** - Diagramas Visuais
   - Arquitetura geral
   - Fluxos de execução
   - Estados do workflow
   - Ciclo de vida de atividades
   - Interação entre componentes

5. **[EXAMPLES.md](EXAMPLES.md)** - Exemplos Práticos
   - 10+ exemplos de uso
   - Casos de uso reais
   - Código comentado
   - Dicas e boas práticas

### 🔧 Referência

6. **[FAQ.md](FAQ.md)** - Perguntas Frequentes
   - Problemas comuns e soluções
   - Configuração e instalação
   - Execução e debugging
   - Performance e escalabilidade
   - Segurança

7. **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guia de Contribuição
   - Como contribuir
   - Padrões de código
   - Processo de Pull Request
   - Áreas para contribuição

## 📂 Arquivos de Código

### Código Principal

- **[config.py](config.py)** - Configurações centralizadas
- **[swf_client.py](swf_client.py)** - Cliente AWS SWF
- **[decision_worker.py](decision_worker.py)** - Orquestrador do workflow
- **[activity_worker.py](activity_worker.py)** - Executor de atividades
- **[workflow_starter.py](workflow_starter.py)** - Iniciador de workflows
- **[setup.py](setup.py)** - Script de configuração inicial

### Configuração

- **[requirements.txt](requirements.txt)** - Dependências Python
- **[.env.example](.env.example)** - Exemplo de configuração
- **[.gitignore](.gitignore)** - Arquivos ignorados pelo Git

## 🗺️ Roteiro de Aprendizado

### Iniciante

1. Leia [QUICKSTART.md](QUICKSTART.md)
2. Execute o exemplo básico
3. Consulte [FAQ.md](FAQ.md) para dúvidas

### Intermediário

1. Leia [README.md](README.md) completo
2. Estude [ARCHITECTURE.md](ARCHITECTURE.md)
3. Explore [EXAMPLES.md](EXAMPLES.md)
4. Visualize [DIAGRAMS.md](DIAGRAMS.md)

### Avançado

1. Leia todo o código fonte com comentários
2. Customize atividades e lógica de decisão
3. Implemente novos padrões
4. Contribua seguindo [CONTRIBUTING.md](CONTRIBUTING.md)

## 🎯 Por Caso de Uso

### Quero executar meu primeiro workflow
→ [QUICKSTART.md](QUICKSTART.md)

### Quero entender como funciona
→ [ARCHITECTURE.md](ARCHITECTURE.md) + [DIAGRAMS.md](DIAGRAMS.md)

### Tenho um problema específico
→ [FAQ.md](FAQ.md)

### Quero ver exemplos de código
→ [EXAMPLES.md](EXAMPLES.md)

### Quero contribuir
→ [CONTRIBUTING.md](CONTRIBUTING.md)

### Preciso de referência rápida
→ [README.md](README.md) seção "Uso"

## 📞 Suporte

- **Issues**: Abra uma issue no repositório
- **Documentação AWS**: [AWS SWF Docs](https://docs.aws.amazon.com/swf/)
- **Boto3 Reference**: [Boto3 SWF](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/swf.html)

## 🔄 Atualizações

Esta documentação é mantida junto com o código. Sempre consulte a versão mais recente no repositório.

---

**Dica**: Use Ctrl+F (ou Cmd+F no Mac) para buscar termos específicos em qualquer documento!
