# Guia de Contribuição

Obrigado por considerar contribuir com este projeto! Este documento fornece diretrizes para colaboração.

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
- [Padrões de Código](#padrões-de-código)
- [Processo de Pull Request](#processo-de-pull-request)
- [Reportando Bugs](#reportando-bugs)
- [Sugerindo Melhorias](#sugerindo-melhorias)

## 🤝 Código de Conduta

Este projeto adere a um código de conduta. Ao participar, você concorda em manter um ambiente respeitoso e colaborativo.

## 🚀 Como Contribuir

### 1. Fork e Clone

```bash
# Fork o repositório no GitHub
# Clone seu fork
git clone https://github.com/seu-usuario/poc-swfaws.git
cd poc-swfaws
```

### 2. Configure o Ambiente

```bash
# Crie ambiente virtual
python -m venv venv

# Ative o ambiente
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt
```

### 3. Crie uma Branch

```bash
git checkout -b feature/minha-contribuicao
```

### 4. Faça suas Alterações

- Escreva código limpo e documentado
- Adicione comentários explicativos
- Siga os padrões de código do projeto

### 5. Teste suas Alterações

```bash
# Execute os testes (quando disponíveis)
python -m pytest

# Teste manualmente
python setup.py
python decision_worker.py  # Em um terminal
python activity_worker.py  # Em outro terminal
python workflow_starter.py # Em um terceiro terminal
```

### 6. Commit e Push

```bash
git add .
git commit -m "feat: adiciona nova funcionalidade X"
git push origin feature/minha-contribuicao
```

### 7. Abra um Pull Request

- Vá para o repositório original no GitHub
- Clique em "New Pull Request"
- Selecione sua branch
- Descreva suas alterações detalhadamente

## 📝 Padrões de Código

### Estilo Python

- Siga PEP 8
- Use 4 espaços para indentação
- Máximo de 100 caracteres por linha
- Use docstrings para funções e classes

### Exemplo de Docstring

```python
def minha_funcao(parametro1, parametro2):
    """
    Breve descrição da função.
    
    Descrição mais detalhada do que a função faz,
    incluindo comportamentos especiais.
    
    Args:
        parametro1 (tipo): Descrição do parâmetro 1
        parametro2 (tipo): Descrição do parâmetro 2
        
    Returns:
        tipo: Descrição do retorno
        
    Raises:
        Exception: Quando ocorre erro X
    """
    pass
```

### Nomenclatura

- **Classes**: PascalCase (`ActivityWorker`)
- **Funções**: snake_case (`poll_for_activity_task`)
- **Constantes**: UPPER_SNAKE_CASE (`WORKFLOW_NAME`)
- **Variáveis**: snake_case (`workflow_id`)

### Comentários

```python
# Comentários de linha única para explicações breves

"""
Comentários de múltiplas linhas para
explicações mais detalhadas ou blocos
de código complexos.
"""
```

## 🔄 Processo de Pull Request

### Checklist

Antes de submeter um PR, verifique:

- [ ] Código segue os padrões do projeto
- [ ] Todos os testes passam
- [ ] Documentação foi atualizada
- [ ] Comentários foram adicionados
- [ ] Commit messages são descritivas
- [ ] Não há conflitos com a branch main

### Formato de Commit Messages

Use o padrão Conventional Commits:

```
tipo(escopo): descrição curta

Descrição mais detalhada se necessário.

Fixes #123
```

**Tipos:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Alterações na documentação
- `style`: Formatação, ponto e vírgula, etc
- `refactor`: Refatoração de código
- `test`: Adição ou correção de testes
- `chore`: Tarefas de manutenção

**Exemplos:**

```
feat(activity): adiciona nova atividade de validação

Implementa validação de CPF/CNPJ na atividade ValidateInput.
Inclui testes unitários e documentação.

Closes #45
```

```
fix(decision): corrige retry infinito em falhas

O contador de retry não estava sendo incrementado corretamente,
causando loops infinitos. Agora limita a 3 tentativas.

Fixes #67
```

## 🐛 Reportando Bugs

### Antes de Reportar

- Verifique se o bug já foi reportado
- Confirme que é realmente um bug
- Colete informações sobre o ambiente

### Template de Bug Report

```markdown
**Descrição do Bug**
Descrição clara e concisa do problema.

**Como Reproduzir**
1. Execute '...'
2. Configure '...'
3. Observe '...'

**Comportamento Esperado**
O que deveria acontecer.

**Comportamento Atual**
O que está acontecendo.

**Screenshots**
Se aplicável, adicione screenshots.

**Ambiente:**
- OS: [Windows 10, Ubuntu 20.04, etc]
- Python: [3.8, 3.9, 3.10]
- Versão do projeto: [commit hash ou tag]

**Logs**
```
Cole logs relevantes aqui
```

**Contexto Adicional**
Qualquer outra informação relevante.
```

## 💡 Sugerindo Melhorias

### Template de Feature Request

```markdown
**Problema a Resolver**
Descrição clara do problema ou necessidade.

**Solução Proposta**
Como você imagina que isso deveria funcionar.

**Alternativas Consideradas**
Outras abordagens que você considerou.

**Contexto Adicional**
Screenshots, exemplos, referências, etc.
```

## 🎯 Áreas para Contribuição

### Funcionalidades Desejadas

- [ ] Testes unitários e de integração
- [ ] Métricas e monitoramento
- [ ] Interface web para visualização
- [ ] Suporte a múltiplos workflows
- [ ] Persistência de estado em banco de dados
- [ ] Notificações por email/SMS
- [ ] Dashboard de monitoramento
- [ ] Documentação de API

### Melhorias de Código

- [ ] Tratamento de erros mais robusto
- [ ] Logging estruturado
- [ ] Configuração via arquivo YAML
- [ ] Suporte a diferentes ambientes (dev/staging/prod)
- [ ] Containerização com Docker
- [ ] CI/CD pipeline

### Documentação

- [ ] Tutoriais passo a passo
- [ ] Exemplos de uso avançado
- [ ] Diagramas de arquitetura
- [ ] Vídeos explicativos
- [ ] FAQ expandido
- [ ] Tradução para outros idiomas

## 📚 Recursos Úteis

- [Documentação AWS SWF](https://docs.aws.amazon.com/swf/)
- [PEP 8 - Style Guide](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Padrão SAGA](https://microservices.io/patterns/data/saga.html)

## ❓ Dúvidas

Se tiver dúvidas sobre como contribuir:

1. Abra uma issue com a tag `question`
2. Descreva sua dúvida claramente
3. Aguarde resposta da comunidade

## 🙏 Agradecimentos

Obrigado por contribuir! Sua ajuda torna este projeto melhor para todos.
