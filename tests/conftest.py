"""Shared test settings. The copy-quality gate (email_lint, LINT_MIN_SCORE) is switched off for tests that exercise
scheduling, sending and pipeline logic with deliberately short fixture emails; tests/test_email_lint.py turns it on."""

import pytest


@pytest.fixture(autouse=True)
def _no_copy_gate(monkeypatch):
    monkeypatch.setenv("LINT_MIN_SCORE", "0")
