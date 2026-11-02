"""Shared test settings.
- The copy-quality gate (email_lint, LINT_MIN_SCORE) is off for tests that exercise scheduling, sending and pipeline
  logic with deliberately short fixture emails; tests/test_email_lint.py turns it on.
- AI_SALES_TRUST_VERIFIED=1 lets fixtures save 'verified' contacts directly; tests/test_hallucination_guards.py turns it
  off to prove that, in real use, only a verifier can mark an address verified."""

import pytest


@pytest.fixture(autouse=True)
def _test_defaults(monkeypatch):
    monkeypatch.setenv("LINT_MIN_SCORE", "0")
    monkeypatch.setenv("AI_SALES_TRUST_VERIFIED", "1")
