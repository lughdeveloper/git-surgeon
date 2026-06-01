# git-surgeon 🔪

[![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange?style=flat-square)](pyproject.toml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000?style=flat-square)](https://github.com/psf/black)

> **Analyze Git repositories and generate visual health reports directly in your terminal.**

`git-surgeon` is a Python CLI that performs deep analysis of local Git repositories — revealing productivity patterns, hidden file coupling, inactive contributors, and project momentum. Everything rendered beautifully in the terminal.

---

## Demo

```
╭──────────────────────────────────────────────────╮
│              git-surgeon · Health Report          │
│  Repo: my-project   Branch: main   Commits: 1243 │
╰──────────────────────────────────────────────────╯

📊 Commits by hour of day
  09h  ████████░░  76
  10h  ██████████  94  ← peak
  14h  ███████░░░  68
  22h  ██░░░░░░░░  18

🔗 Files with highest coupling
  src/auth.ts      ↔  src/middleware.ts    (47 commits together)
  src/db.ts        ↔  src/models.ts        (35 commits together)

👻 Ghost contributors
  maria@dev.com       — 312 commits — last seen 8 months ago
  joao@example.com    — 145 commits — last seen 6 months ago

⚡ Most volatile files
  src/api.ts          — 156 commits
  src/utils.ts        — 89 commits

📈 Project velocity
  Last 30 days:       43 commits
  Previous 30 days:   38 commits
  Change:             +13.1% ↑

╭──────────────────────────────────────────────────╮
│       Health Score: 78 / 100  ·  Healthy ✓       │
╰──────────────────────────────────────────────────╯
```

---

## Features

| Analysis | What it does |
|---|---|
| **Commits by hour** | Maps productivity peaks and detects unhealthy work patterns |
| **Co-change analysis** | Finds files that always change together — revealing hidden coupling |
| **Ghost contributors** | Lists authors inactive for 90+ days |
| **Volatile files** | Top files by commit count — likely hotspots and instability sources |
| **Project velocity** | Compares last 30 days vs previous 30 days |
| **Health score** | Single 0–100 score with classification: Critical / Regular / Healthy / Excellent |

---

## Installation

**Requirements:** Python 3.10+ and Git

```bash
# Clone and install
git clone https://github.com/lughdeveloper/git-surgeon.git
cd git-surgeon
pip install -e .

# Verify
git-surgeon --help
```

For development (includes tests, linter, type checker):

```bash
pip install -e ".[dev]"
```

---

## Usage

```bash
# Basic analysis
git-surgeon analyze ./my-project

# Filter by date
git-surgeon analyze ./my-project --since 2024-01-01

# Filter by author
git-surgeon analyze ./my-project --author "maria@example.com"

# Export to HTML
git-surgeon analyze ./my-project --export report.html

# Change result limit (default: 10)
git-surgeon analyze ./my-project --top 20

# Combine flags
git-surgeon analyze ./my-project \
  --since 2024-06-01 \
  --author "joao" \
  --export report.html \
  --top 15

# Verbose / debug mode
git-surgeon analyze ./my-project --verbose

# Show version
git-surgeon version
```

---

## How the health score works

The score starts at 100 and deductions are applied based on findings:

| Factor | Max deduction | Trigger |
|---|---|---|
| Work-life balance | −20 pts | Commits heavily concentrated in off-hours |
| File coupling | −25 pts | High co-change ratio between file pairs |
| Team continuity | −20 pts | Ghost contributors detected |
| File stability | −20 pts | One file accounts for >30% of all changes |
| Project momentum | −15 pts | Velocity drop >30% or spike >50% |

**Score classification:**

| Score | Status |
|---|---|
| 80–100 | ✅ Excellent |
| 60–79 | ✓ Healthy |
| 40–59 | ⚠️ Regular |
| 0–39 | ❌ Critical |

---

## Project structure

```
git-surgeon/
├── git_surgeon/
│   ├── cli.py                   # CLI entry point (Typer)
│   ├── analyzer.py              # Git parser core
│   ├── reporter.py              # Terminal rendering (Rich) + HTML export
│   └── metrics/
│       ├── commits_by_hour.py
│       ├── cochange.py
│       ├── ghost_contributors.py
│       ├── volatile_files.py
│       ├── velocity.py
│       └── health_score.py
├── tests/
│   └── test_metrics.py
├── pyproject.toml
├── LICENSE
└── .gitignore
```

---

## Development

```bash
# Setup
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
pip install -e ".[dev]"

# Run tests
pytest
pytest --cov=git_surgeon   # with coverage

# Code quality
black git_surgeon/ tests/
ruff check git_surgeon/ tests/
mypy git_surgeon/
```

Commits follow [Conventional Commits](https://www.conventionalcommits.org/):
`feat:` `fix:` `docs:` `test:` `refactor:`

---

## Troubleshooting

**"Not a valid Git repository"**
Make sure the path points to the root of the repo, not the `.git` folder:
```bash
git-surgeon analyze ./my-project      # correct
git-surgeon analyze ./my-project/.git # wrong
```

**"No commits found"**
The repo may be empty or the `--since` date too recent.

**Permission error on Windows**
Run the terminal as Administrator.

---

## Use cases

- **Pre-refactor review** — use co-change analysis to find modules that should be merged or decoupled
- **Team onboarding** — show new devs the health report to understand project history at a glance
- **Burnout detection** — monitor commit hours to spot unhealthy work patterns
- **Stakeholder reports** — export to HTML and share project health with non-technical stakeholders
- **Periodic tracking** — run weekly and compare reports to track evolution over time

---

## Contributing

1. Fork the project
2. Create your branch: `git checkout -b feat/your-feature`
3. Commit with semantic messages
4. Push: `git push origin feat/your-feature`
5. Open a Pull Request

Please keep test coverage above 80% and use type hints throughout.

---

## Tech stack

- [GitPython](https://github.com/gitpython-developers/GitPython) — Git repository parsing
- [Typer](https://github.com/tiangolo/typer) — CLI framework
- [Rich](https://github.com/Textualize/rich) — Terminal rendering
- [Pydantic](https://github.com/pydantic/pydantic) — Data validation

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

*Built to make Git analysis fast, visual, and actually useful.*
