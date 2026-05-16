"""Test session bootstrap: load .env.test, validate, clear settings cache.

Env loading runs BEFORE any tradegod import to guarantee get_settings()'s
lru_cache is never primed against process env before .env.test overrides it.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

_ = load_dotenv(Path(__file__).resolve().parent.parent / ".env.test", override=False)

if not os.environ.get("TEST_DATABASE_URL"):
    pytest.exit("TEST_DATABASE_URL is not set; cannot run tests.", returncode=2)

# import after env load so the cache primes against test env, not process env
from tradegod.core.settings import get_settings  # noqa: E402

get_settings.cache_clear()
