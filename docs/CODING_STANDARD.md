# Coding Standard

DistanceCalculatorPro

Version 1.0

---

# CS-001

Follow PEP8.

---

# CS-002

Use type hints everywhere.

Good

def calculate(
    request: RouteRequest
) -> RouteResult:

Bad

def calculate(request):

---

# CS-003

Constructor Injection only.

Never instantiate dependencies inside business classes.

---

# CS-004

Prefer immutable models.

Use

@dataclass(
    frozen=True,
    slots=True
)

whenever possible.

---

# CS-005

Private members begin with "_".

Example

_provider

_engine

_browser

---

# CS-006

One class.

One responsibility.

---

# CS-007

Maximum nesting

Target

3

Prefer early return.

---

# CS-008

Functions should describe behavior.

Good

calculate()

validate()

build_requests()

Bad

do_work()

process()

handle()

---

# CS-009

Avoid boolean parameters.

Bad

calculate(True)

Prefer

calculate(
    alternatives=True
)

---

# CS-010

Do not use magic numbers.

Bad

timeout=30

Good

DEFAULT_TIMEOUT

---

# CS-011

Prefer explicit code.

Avoid hidden side effects.

---

# CS-012

Raise exceptions.

Never return None for failures.

---

# CS-013

Do not catch Exception unless rethrowing or adding context.

---

# CS-014

Comments explain WHY.

Never explain WHAT.

---

# CS-015

Imports

Standard Library

↓

Third Party

↓

Project

---

# CS-016

Avoid circular dependencies.

---

# CS-017

Avoid global mutable state.

---

# CS-018

Properties

Properties expose state.

They should not perform business logic.

---

# CS-019

Logging

Business events only.

Do not log every helper function.

---

# CS-020

Prefer composition over inheritance.

---

# CS-021

Dependency Rule

Higher layers never depend on lower implementation details.

Controller

↓

Service

↓

Provider

↓

Engine

Never reverse the dependency.

---

# CS-022

Testing

Every public method must have

- success test
- failure test
- edge case

---

# CS-023

Mock only external systems.

Never mock value objects.

---

# CS-024

Every bug fix requires a regression test.

---

# CS-025

Refactoring Rule

If behavior does not change

↓

Tests should require little or no modification.

Large test rewrites indicate the refactor may have coupled tests to implementation.

---

# CS-026

Code Review Checklist

□ SOLID respected

□ DI respected

□ No duplicated code

□ Readable

□ Testable

□ No hidden dependency

□ No unnecessary abstraction

□ No over-engineering

□ 100% tests pass

□ 100% coverage maintained