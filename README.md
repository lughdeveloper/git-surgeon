# 🔪 git-surgeon

[![Python Version](https://img.shields.io/badge/python-3.10+-blue?style=flat-square)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000?style=flat-square)](https://github.com/psf/black)

> Analyze Git repositories and generate visual health reports directly in your terminal.

**git-surgeon** é uma ferramenta CLI em Python que realiza análise profunda de repositórios Git locais, gerando relatórios visuais de "saúde" do projeto. Identifique padrões de desenvolvimento, detecte acoplamento implícito entre arquivos, acompanhe contribuidores inativos e muito mais.

## 📊 O que o git-surgeon faz

### Análises Incluídas

#### 1. **Commits por Hora do Dia** 📊

Visualiza em quais horários o desenvolvedor é mais produtivo, ajudando a identificar padrões de trabalho e possíveis sinais de burnout.

```
📊 Commits por hora do dia
  00h ██░░░░░░░░  12
  14h ████████░░  87  ← pico
  ...
```

#### 2. **Arquivos com Maior Acoplamento** 🔗

Identifica pares de arquivos que frequentemente mudam juntos, revelando dependências ocultas e possíveis problemas de design.

```
🔗 Arquivos com maior acoplamento
  src/auth.ts  ↔  src/middleware.ts   (47x)
  src/db.ts    ↔  src/models.ts       (35x)
```

#### 3. **Contribuidores Fantasmas** 👻

Detecta autores que tiveram atividade significativa mas não contribuem há mais de 90 dias.

```
👻 Contribuidores fantasmas
  maria@dev.com — 312 commits — inativo há 8 meses
  joão@example.com — 145 commits — inativo há 6 meses
```

#### 4. **Arquivos Mais Voláteis** ⚡

Top 10 arquivos mais alterados, indicando possíveis pontos de instabilidade no projeto.

```
⚡ Arquivos mais voláteis
  src/api.ts — 156 commits
  src/utils.ts — 89 commits
```

#### 5. **Velocidade do Projeto** 📈

Compara commits dos últimos 30 dias vs 30 dias anteriores, mostrando se o projeto está acelerando, estável ou desacelerando.

```
📈 Velocidade do Projeto
  Últimos 30 dias: 43 commits
  30 dias anteriores: 38 commits
  Variação: +13.1% ↑
```

#### 6. **Score de Saúde Geral** 💪

Calcula um score de 0 a 100 baseado em todos os indicadores, com classificação: **Crítico / Regular / Saudável / Excelente**

```
╭─────────────────────────────────────╮
│  Score de Saúde: 78/100  · Saudável ✓  │
╰─────────────────────────────────────╯
```

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.10+
- Git

### Instalação com pip (do repositório local)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/git-surgeon.git
cd git-surgeon

# Instale em modo development
pip install -e .

# Para instalar também as dependências de desenvolvimento
pip install -e ".[dev]"
```

### Verificar instalação

```bash
git-surgeon --help
```

---

## 📖 Uso

### Comando Básico

```bash
git-surgeon analyze ./meu-projeto
```

### Exemplos Avançados

#### Analisar a partir de uma data específica

```bash
git-surgeon analyze ./projeto --since 2024-01-01
```

#### Filtrar por autor

```bash
git-surgeon analyze ./projeto --author "maria@example.com"
```

#### Exportar para HTML

```bash
git-surgeon analyze ./projeto --export report.html
```

#### Personalizar limite de resultados

```bash
git-surgeon analyze ./projeto --top 20
```

#### Combinar múltiplas flags

```bash
git-surgeon analyze ./projeto \
  --since 2024-06-01 \
  --author "joão" \
  --export report.html \
  --top 15
```

#### Modo verbose (debug)

```bash
git-surgeon analyze ./projeto --verbose
```

---

## 📐 Como Funcionam as Métricas

### 📊 Commits por Hora

**O que avalia:** Distribuição de commits ao longo do dia (0-23h)

**Por quê:** Ajuda a identificar:

- Picos de produtividade
- Sinais de overwork (commits em horas irregulares)
- Padrões saudáveis de trabalho

**Impacto no Score:** -20 pontos se muito concentrado em poucas horas

---

### 🔗 Co-change Analysis

**O que avalia:** Frequência com que pares de arquivos mudam juntos

**Por quê:**

- Acoplamento implícito indica possíveis problemas de design
- Arquivos que mudam juntos frequentemente talvez devessem ser um módulo único
- Ajuda a refatorar e reorganizar a arquitetura

**Impacto no Score:** -25 pontos se alta coesão entre arquivos

---

### 👻 Contribuidores Fantasmas

**O que avalia:** Autores sem commits há mais de 90 dias

**Por quê:**

- Indica rotatividade de team ou abandono de projeto
- Importante para entender continuidade do projeto
- Afeta a manutenibilidade futura

**Impacto no Score:** -20 pontos por cada contribuidor inativo

---

### ⚡ Arquivos Voláteis

**O que avalia:** Arquivos que recebem mais commits

**Por quê:**

- Arquivos muito modificados podem ser instáveis
- Podem indicar requisitos fluidos ou design inadequado
- Bons candidatos para testes e revisão de código

**Impacto no Score:** -20 pontos se um arquivo tem >30% de todas as mudanças

---

### 📈 Velocidade

**O que avalia:** Comparação de commits nos últimos 30 vs 30 dias anteriores

**Por quê:**

- Indica se o projeto está ganhando ou perdendo momentum
- Detecta desaceleração que pode indicar problemas
- Mostra crescimento insustentável

**Impacto no Score:** -15 pontos se declínio >30% ou crescimento >50%

---

### 💪 Score de Saúde

**Fórmula:**

```
Score = 100 - (work_life_balance + coupling + team_continuity + stability + momentum)
```

**Classificação:**
| Score | Classificação |
|-------|---------------|
| 80-100 | ✅ Excelente |
| 60-79 | ✓ Saudável |
| 40-59 | ⚠️ Regular |
| 0-39 | ❌ Crítico |

---

## 🏗️ Estrutura do Projeto

```
git-surgeon/
├── git_surgeon/
│   ├── __init__.py              # Package info
│   ├── cli.py                   # CLI entry point (typer)
│   ├── analyzer.py              # Core Git parser
│   ├── reporter.py              # Rich rendering + HTML export
│   └── metrics/
│       ├── __init__.py
│       ├── commits_by_hour.py   # Distribuição horária
│       ├── cochange.py          # Análise de co-change
│       ├── ghost_contributors.py # Contribuidores inativos
│       ├── volatile_files.py    # Arquivos voláteis
│       ├── velocity.py          # Momentum do projeto
│       └── health_score.py      # Cálculo do score final
├── tests/
│   └── test_metrics.py          # Testes unitários
├── pyproject.toml               # Configuração do projeto
├── README.md                    # Este arquivo
├── LICENSE                      # MIT License
└── .gitignore
```

---

## 🛠️ Desenvolvimento

### Setup para Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/git-surgeon.git
cd git-surgeon

# Crie um virtual environment
python -m venv venv

# Ative o venv
# No Windows:
venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate

# Instale em modo development com testes
pip install -e ".[dev]"
```

### Rodando Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=git_surgeon

# Modo verbose
pytest -v
```

### Formatação de Código

```bash
# Black para formatação
black git_surgeon/ tests/

# Ruff para linting
ruff check git_surgeon/ tests/

# MyPy para type checking
mypy git_surgeon/
```

---

## 📝 Commits Semânticos

Ao contribuir, use commits semânticos:

```bash
git commit -m "feat: adiciona nova métrica de qualidade"
git commit -m "fix: corrige parsing de commits inválidos"
git commit -m "docs: melhora documentação do reporter"
git commit -m "test: adiciona testes para velocity"
git commit -m "refactor: simplifica lógica de health score"
```

---

## 🐛 Troubleshooting

### "Not a valid Git repository"

```bash
# Certifique-se de que o caminho aponta para um repositório Git
git-surgeon analyze /caminho/para/repo/.git  # ❌ Errado
git-surgeon analyze /caminho/para/repo      # ✅ Correto
```

### "No commits found"

O repositório pode estar vazio ou o filtro `--since` pode ser muito recente.

### Erro de permissão

```bash
# No Windows, execute como administrador
# No Linux/Mac, verifique permissões da pasta
chmod -R u+r /caminho/para/repo
```

---

## 📊 Casos de Uso Reais

### 1. **Code Review Pré-Refatoração**

Use a análise de co-change para identificar módulos que precisam ser reorganizados.

### 2. **Onboarding de Novos Desenvolvedores**

Mostre o relatório para que entendam a "saúde" e padrões do projeto.

### 3. **Detecção de Burnout**

Monitore os commits por hora para identificar padrões não-saudáveis na equipe.

### 4. **Relatórios de Produto/Negócio**

Exporte para HTML e compartilhe com stakeholders a saúde do projeto.

### 5. **Acompanhamento de Projeto**

Execute periodicamente e compare relatórios para acompanhar a evolução.

### 6. **Identificação de Dependências**

Use a análise de acoplamento para remover duplicações e dependências ocultas.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feat/amazing-feature`)
3. Commit com mensagens semânticas
4. Push para a branch (`git push origin feat/amazing-feature`)
5. Abra um Pull Request

### Diretrizes de Contribuição

- Escreva código limpo e bem documentado
- Adicione testes para novas funcionalidades
- Mantenha a cobertura acima de 80%
- Use type hints em todo o código Python
- Siga o estilo de código (black + ruff)

---

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja [LICENSE](LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- [GitPython](https://github.com/gitpython-developers/GitPython) - Para parsing de Git
- [Typer](https://github.com/tiangolo/typer) - Para CLI elegante
- [Rich](https://github.com/Textualize/rich) - Para output visual no terminal
- [Pydantic](https://github.com/pydantic/pydantic) - Para validação de dados

---

## 📞 Suporte

Encontrou um bug ou tem uma sugestão? Abra uma [issue no GitHub](https://github.com/seu-usuario/git-surgeon/issues).

---

**Feito com 🔪 para tornar sua análise de Git mais fácil e intuitiva.**
