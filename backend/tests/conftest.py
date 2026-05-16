"""Test session bootstrap: load .env.test, validate, clear settings cache."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from tradegod.core.settings import get_settings

_ = load_dotenv(Path(__file__).resolve().parent.parent / ".env.test", override=False)

if not os.environ.get("TEST_DATABASE_URL"):
    pytest.exit("TEST_DATABASE_URL is not set; cannot run tests.", returncode=2)

get_settings.cache_clear()
