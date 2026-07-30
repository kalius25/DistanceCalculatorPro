# Testing Guidelines

Version 1.0

---

# Philosophy

Test behavior.

Not implementation.

---

# Unit Tests

Every class has

- constructor tests
- happy path
- failure path
- edge cases

---

# Mocking

Mock only external dependencies.

Do NOT mock value objects.

---

# Assertions

One behavior per test.

Good

test_calculate_returns_failed_result()

Bad

test_everything()

---

# Private Methods

Do not test private methods directly.

Exception

Pure helper algorithms that are intentionally static.

---

# Coverage

Required

100%

Statement

100%

Branch

100%

---

# Test Naming

test_<method>_<behavior>

Examples

test_calculate_success()

test_calculate_provider_error()

test_validate_empty_origin()

---

# Arrange

Act

Assert

Use AAA consistently.

---

# No Real Infrastructure

No browser

No Excel

No Google Maps

No filesystem

No network

---

# Regression Tests

Every bug fixed

↓

Add one test.

---

# Refactoring Rule

Tests should change only when behavior changes.

Refactoring without behavior change should not require rewriting large numbers of tests.

If many tests break after a simple refactor,

reconsider the refactor.

---

# Quality Gate

A Pull Request is accepted only if

✓ All tests pass

✓ Coverage remains 100%

✓ No new architecture violations

✓ Dependency Injection preserved

✓ No over-engineering introduced
