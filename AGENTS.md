# AGENTS.md – fiesta.plus

Guidelines for AI coding agents (Copilot, Claude, Cursor, etc.) working in this repository.

---

## Project Overview

**fiesta.plus** is a production Django application — the social network to match buddies with international students. Used by sections of [ESN (Erasmus Student Network)](https://esn.org). Deployed at [fiesta.plus](https://fiesta.plus).

> ⚠️ This project is in active development.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12+ |
| Framework | Django 4.2 |
| Package manager | Poetry (`pyproject.toml` + `poetry.lock`) |
| Settings system | `django-configurations` (class-based, mixin composition) |
| Database | PostgreSQL 15 (+ SQLite for wiki) |
| Task queue | Celery + Redis |
| Frontend | HTMX + Webpack/Yarn + `django-webpack-loader` |
| Auth | `django-allauth` + ESN CAS SSO (custom fork) + Google OAuth |
| Static files | WhiteNoise / S3 (production) |
| Dev environment | Docker Compose; all commands via `make` |
| Local domain | `*.fiesta.test` (nginx-proxy + mkcert) |
| CI/CD | GitHub Actions (`deploy.yml`) |

---

## Repository Layout

```
fiesta-plus/
├── fiesta/               # Django project root (contains manage.py)
│   ├── apps/             # Feature apps (see below)
│   ├── fiesta/           # Core Django package (settings, urls, wsgi, asgi)
│   │   └── settings/     # Settings split by concern, composed via django-configurations
│   ├── static/           # Static assets
│   └── templates/        # Global Django templates
├── conf/                 # Deployment configs (k8s, certs)
├── nginx/                # nginx + docker-proxy config
├── webpack/              # JS bundling (Webpack + Yarn)
├── charts/               # Helm charts (Kubernetes deployment)
├── docs/                 # Git submodule → wiki repo
├── .github/workflows/    # CI/CD (GitHub Actions)
├── .env.template         # Copy to .env and fill in secrets
├── docker-compose.yml    # Full dev environment
├── docker-compose.override.yml
├── docker-compose.prod.yml
├── Dockerfile            # Multi-stage: web, proxy, webpack, wiki
├── Makefile              # Primary developer interface
└── pyproject.toml        # Project metadata + all tool configuration
```

### Feature Apps (`fiesta/apps/`)

| App | Purpose |
|-----|---------|
| `accounts` | User accounts and profiles |
| `buddy_system` | Core feature: buddy–student matching |
| `dashboard` | Section dashboard views |
| `esnaccounts` | ESN Accounts CAS SSO provider |
| `esncards` | ESN card management |
| `events` | Event management |
| `fiestaforms` | Shared form utilities and widgets |
| `fiestarequests` | Request/approval workflow abstractions |
| `fiestatables` | `django-tables2` integration helpers |
| `files` | File upload/download handling |
| `pages` | Static/flat pages |
| `pickup_system` | Airport pickup coordination |
| `plugins` | Plugin registry & per-section feature management (**key architectural component**) |
| `public` | Public-facing pages (landing, section homepages) |
| `sections` | ESN sections, section spaces, memberships |
| `universities` | University database |
| `utils` | Shared utilities |
| `wiki` | Wiki fetcher integration |

---

## Settings Architecture

Settings use **`django-configurations`** — class-based with mixin composition. Activated via the `DJANGO_CONFIGURATION` env var.

```
fiesta/fiesta/settings/
├── __init__.py      ← Configuration classes: Base, Development, LocalProduction, Production
├── project.py       ← INSTALLED_APPS, MIDDLEWARE, core project settings
├── auth.py          ← allauth, CAS, social auth
├── db.py            ← PostgreSQL + wiki SQLite
├── files.py         ← local media files vs S3 (production)
├── logging.py       ← logging + Sentry
├── notifications.py ← email/mailer config
├── security.py
├── templates.py
└── _utils.py
```

| Class | Purpose |
|-------|---------|
| `Development` | `DEBUG=True`, debug toolbar, `ROOT_DOMAIN=fiesta.test` |
| `LocalProduction` | `DEBUG=False`, local domain, no S3/Sentry |
| `Production` | `DEBUG=False`, S3 storage, Sentry, SMTP, `DATABASE_URL` from env |

---

## Development Commands

All commands go through Docker Compose via `make`. The `web` service runs Django.

### Quick start

```bash
git clone git@github.com:esnvutbrno/fiesta-plus.git
cd fiesta-plus

# Copy env template and fill in at minimum DJANGO_SECRET_KEY
cp .env.template .env

# Build and start everything
make upb

# Apply migrations
make migrate

# Seed with fake data (optional)
make seed
```

### Common `make` targets

```bash
make upd              # Start all containers (detached)
make upb              # Build + start containers
make build            # Build Docker images only
make migrate          # Run manage.py migrate
make makemigrations   # Run manage.py makemigrations
make showmigrations   # Show migration state
make test             # Run tests (--keepdb --parallel)
make seed             # Seed DB with fake data
make shell_plus       # django-extensions shell_plus
make check            # Run all Django system checks
make pre-commit       # Run all linters/formatters
make psql             # Open PostgreSQL shell
make dumpdb           # Dump DB to dated .sql file
make loaddb dump=FILE # Load DB from a dump
make graph_models     # Generate models.png
make startplugin name=NAME  # Scaffold a new plugin app
make generate-local-certs   # Generate *.fiesta.test TLS certs via mkcert
```

```bash
# Run any manage.py command:
make da cmd=shell

# Run any docker compose command:
make dc cmd="ps"
```

---

## Code Style & Conventions

- **Line length**: 120 characters
- **Formatter**: `black` (excludes migrations)
- **Import sorting**: `isort` with `--profile black`; `from __future__ import annotations` required in all files
- **Linter**: `ruff` (rules `UP, DJ, PIE, INT, PTH, SIM, RET, G, DTZ, B`, ignores `E731`)
- **Security**: `bandit -iii -ll`
- **Template linting**: `djlint --profile django`
- **Type checker**: `mypy`

All of the above run automatically via **pre-commit** (`make pre-commit`).

### Django conventions

- Each feature lives in its own app under `fiesta/apps/`
- Standard app layout: `models.py` (or `models/`), `views.py` (or `views/`), `forms.py`, `urls.py`, `admin.py`
- Use `factory_boy` + `Faker` for test data — never hardcode fixture data
- Import all models from `models/` sub-packages via `__init__.py`
- Keep all migrations tracked in git (a pre-commit hook enforces this)
- `from __future__ import annotations` is **required** in every Python file (enforced by isort)
- Frontend interactions use **HTMX** for server-driven partial updates; JS bundles via **Webpack**
- Do not add new JS frameworks or bundlers — use the existing Webpack setup in `webpack/`

---

## Plugin Architecture

The `plugins` app is the architectural centrepiece. Features (buddy_system, esncards, events, pickup_system) are **plugins** that can be enabled or disabled per ESN section.

- Scaffold a new plugin: `make startplugin name=<plugin_name>`
- The `CurrentPluginMiddleware` resolves which plugin is active for the current request
- URL routing dynamically includes all enabled plugin apps
- The middleware chain resolves: section (from subdomain) → membership → active plugin → user profile

---

## Testing

- **Framework**: `pytest` + `pytest-django`
- **Settings module**: set via `DJANGO_CONFIGURATION` env var (uses `Development` by default)
- **Run via**: `make test` (runs inside Docker with `--keepdb --parallel --verbosity 1`)
- **Factories**: `factory_boy` + `Faker`

### Rules for agents

1. Always run `make test` before declaring a task complete.
2. Every new validator or business-rule function needs both a **success** and a **failure** test.
3. New behaviour must be covered by tests.
4. When refactoring: verify existing tests pass first, then change the code.
5. Never disable or delete failing tests without explicit human approval.

---

## Branching & Commits

- **Default branch is `develop`** — never commit directly to `develop` or `main`.
- Branch names: `feat-*`, `fix-*`, `chore-*`, `docs-*`, `refactor-*`
- Commit message format: `WHAT(scope): WHY` — imperative mood, single line, no body
  - Examples: `feat(buddy-system): add waitlist support`, `fix(sections): prevent duplicate membership`
- Do **not** commit AI-generated markdown descriptions unless explicitly requested.

---

## Environment Configuration

Copy `.env.template` to `.env` and fill in at minimum:

```bash
DJANGO_CONFIGURATION=Development
DJANGO_SECRET_KEY=<generate a strong key>
ROOT_DOMAIN=fiesta.test
```

Production-only env vars (S3, Sentry, SMTP) are only needed for the `Production` configuration class.

---

## What Agents Should NOT Do

- Do not add Python dependencies without updating `pyproject.toml` via `poetry add <package>`.
- Do not bypass `pre-commit` hooks (`--no-verify`).
- Do not hardcode secrets, credentials, or environment-specific values — use `django-environ` / env variables.
- Do not use `print()` for debugging in production code — use Django's `logging` module.
- Do not commit directly to `develop` or `main`.
- Do not add new JS frameworks or bundlers — use the existing Webpack setup.
- Do not modify migration files manually — always use `manage.py makemigrations`.
