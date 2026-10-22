# automation-task

[![API tests](https://github.com/Anjalipanwar/automation-task/actions/workflows/api-tests.yml/badge.svg)](https://github.com/Anjalipanwar/automation-task/actions/workflows/api-tests.yml)

API tests for the [Toolshop API](https://api.practicesoftwaretesting.com/api/documentation), using **Python**, **pytest** and **Playwright** (`APIRequestContext` only, no UI tests).

## Project layout

```text
framework/
  config.py      # loads settings (BASE_URL, API_TOKEN, TIMEOUT_MS) from .env
  clients/       # thin API clients wrapping APIRequestContext, one per resource
  models/        # pydantic models for response validation
  utils/         # helpers, e.g. faker-based test data
tests/
  conftest.py    # session APIRequestContext, client fixtures, marker registration
  api/           # tests grouped by resource
```

Tests never make raw HTTP calls; they always go through a client in `framework/clients/`.

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync                    # create .venv and install dependencies
cp .env.example .env       # then edit .env with your values
```

No browser install is needed: `APIRequestContext` does not launch a browser.

The brand tests create and delete data, and deleting needs an admin login. Set `ADMIN_EMAIL` and
`ADMIN_PASSWORD` in `.env` (Toolshop's demo accounts are listed at
<https://practicesoftwaretesting.com>). Without them, the brand tests are skipped.

Run `uv run pytest -v -s` to see the fixture setup/teardown order printed.

## Running tests

```bash
uv run pytest              # all tests
uv run pytest -m smoke     # smoke tests only
uv run pytest -m regression
uv run pytest tests/api/test_products.py -v
```

## Adding a new resource

1. Add a client in `framework/clients/<resource>_client.py` extending `BaseClient`.
2. Add pydantic models in `framework/models/<resource>.py`.
3. Add a fixture for the client in `tests/conftest.py`.
4. Add tests in `tests/api/test_<resource>.py`.

## CI

GitHub Actions runs the suite on every push, on pull requests to `main`, and on demand
(Actions → API tests → Run workflow). See [.github/workflows/api-tests.yml](.github/workflows/api-tests.yml).

The brand tests need two repository secrets, `ADMIN_EMAIL` and `ADMIN_PASSWORD`
(Settings → Secrets and variables → Actions). Without them, those tests are skipped.
Each run uploads a JUnit XML report as the `junit-report` artifact.
