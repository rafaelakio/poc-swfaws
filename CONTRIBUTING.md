# Guia de Contribuição

Obrigado por considerar contribuir com este projeto! Este documento descreve o workflow, os padrões de código e o processo de revisão adotados.

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Workflow de Branches](#workflow-de-branches)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Padrões de Código](#padrões-de-código)
- [Conventional Commits](#conventional-commits)
- [Como Criar Pull Requests](#como-criar-pull-requests)
- [Processo de Code Review](#processo-de-code-review)
- [Branch Protection](#branch-protection)
- [Reportando Bugs](#reportando-bugs)
- [Sugerindo Melhorias](#sugerindo-melhorias)

## 🤝 Código de Conduta

Este projeto adere a um código de conduta. Ao participar, você concorda em manter um ambiente respeitoso e colaborativo.

## 🌿 Workflow de Branches

Utilizamos um modelo simples baseado em feature branches:

1. Sempre parta da `main` atualizada (`git pull --ff-only origin main`).
2. Crie uma branch descritiva usando um dos prefixos:
   - `feature/...` — novas funcionalidades
   - `fix/...` — correções de bug
   - `chore/...` — manutenção, tooling, CI, docs secundárias
   - `docs/...` — mudanças apenas de documentação
   - `refactor/...` — refatorações sem mudança de comportamento
   - `test/...` — adição ou ajuste de testes
3. Abra um Pull Request contra `main`.
4. Aguarde revisão (≥1 aprovação) e CI verde.
5. Faça merge (squash ou merge commit, conforme política do repositório).

## ⚙️ Configuração do Ambiente

```bash
# Clone seu fork
git clone https://github.com/seu-usuario/poc-swfaws.git
cd poc-swfaws

# Crie e ative um ambiente virtual
python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

# Instale dependências de runtime e dev
make install-dev

# Instale os git hooks
pre-commit install
```

Use `.env.example` como base para criar seu `.env` local. **Nunca** comite credenciais reais.

## 📝 Padrões de Código

### Estilo Python

- Siga PEP 8.
- Formatação automática com **black** (line length 100).
- Imports organizados com **isort** (perfil `black`).
- Lint com **ruff**.
- Tipagem estática opcional com **mypy**.
- Docstrings para funções e classes públicas.

### Nomenclatura

- **Classes**: PascalCase (`ActivityWorker`)
- **Funções**: snake_case (`poll_for_activity_task`)
- **Constantes**: UPPER_SNAKE_CASE (`WORKFLOW_NAME`)
- **Variáveis**: snake_case (`workflow_id`)

### Testes

- Use **pytest** e coloque arquivos em `tests/`.
- Mocke integrações AWS com **moto** — testes devem rodar offline.
- Mire em ≥70% de cobertura (`make test-cov`).

## 🧾 Conventional Commits

Utilize o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```
tipo(escopo opcional): descrição curta

Corpo opcional explicando motivação e contexto.

Refs: #123
```

**Tipos aceitos:**

| Tipo        | Uso                                               |
|-------------|---------------------------------------------------|
| `feat`      | Nova funcionalidade                               |
| `fix`       | Correção de bug                                   |
| `chore`     | Tarefas de manutenção (build, deps, configs)      |
| `docs`      | Apenas documentação                               |
| `test`      | Adição ou correção de testes                      |
| `refactor`  | Refatoração sem mudança de comportamento          |
| `ci`        | Mudanças em pipelines / automação                 |
| `style`     | Formatação, lint, espaçamento                     |
| `perf`      | Melhorias de performance                          |

**Exemplos:**

```
feat(activity): adiciona ValidateInput com checagem de CPF
fix(decision): corrige contador de retries em falhas
docs(readme): adiciona seção de troubleshooting
test(swf_client): cobre register_domain com moto
chore(ci): habilita workflow de testes no GitHub Actions
```

## 🔁 Como Criar Pull Requests

1. Título descritivo seguindo Conventional Commits.
2. Preencha o template `.github/pull_request_template.md`.
3. Vincule a issue relacionada usando `Closes #N` ou `Refs #N`.
4. Inclua screenshots/recordings quando houver mudança de UX.
5. Garanta que o CI esteja verde antes de pedir revisão.

## 👀 Processo de Code Review

- **≥1 aprovação** de um code owner antes do merge.
- Revisões devem focar em correção, legibilidade, testes e segurança.
- Discussões devem ser resolvidas antes do merge.
- Mudanças solicitadas devem vir em **novos commits** (sem amend em commits já revisados).

## 🔒 Branch Protection

Configuração recomendada em **GitHub → Settings → Branches → Add rule** para `main`:

- **Require a pull request before merging** (dismiss stale approvals ao push).
- **Require approvals**: 1 reviewer (CODEOWNERS).
- **Require status checks to pass before merging** (CI: lint, test).
- **Require branches to be up to date before merging**.
- **Require conversation resolution before merging**.
- **Include administrators** — regras aplicam-se a todos.
- (Opcional) **Require signed commits**.

## 🐛 Reportando Bugs

Use o template [`.github/ISSUE_TEMPLATE/bug_report.md`](.github/ISSUE_TEMPLATE/bug_report.md). Inclua passos de reprodução, comportamento esperado e ambiente.

## 💡 Sugerindo Melhorias

Use o template [`.github/ISSUE_TEMPLATE/feature_request.md`](.github/ISSUE_TEMPLATE/feature_request.md). Explique a motivação, solução proposta e alternativas consideradas.
