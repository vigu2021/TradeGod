# TradeGod backend

## Testing

Prerequisite: create the test database once.

```bash
createdb tradegod_test
```

Set the test DB URL in `backend/.env.test` (alongside the existing `.env`):

```
TEST_DATABASE_URL=postgresql+asyncpg://<user>:<pass>@localhost:5432/tradegod_test
```

Run all tests:

```bash
uv run pytest
```

Unit-only fast lane:

```bash
uv run pytest tests/unit
```

With coverage:

```bash
uv run pytest --cov
```

The first run executes `alembic upgrade head` against the test DB (~1-3s).
