# ARCHITECTURE_DECISIONS.md

DistanceCalculatorPro

Version 1.0

Status: Frozen

---

# ADR-001

## Use Dependency Injection

Status

Accepted

Decision

All business classes receive dependencies through constructors.

Reason

- loose coupling
- easy unit testing
- replace implementations
- explicit dependencies

Example

Correct

CalculationService(provider)

Wrong

CalculationService()
provider = GoogleProvider()

---

# ADR-002

## Business Layer Must Not Create Infrastructure

Status

Accepted

Decision

Controllers, Services and Providers never instantiate infrastructure objects.

Infrastructure includes

- Browser
- WebDriver
- Google Maps Engine
- Excel
- Logger

Reason

Infrastructure changes frequently.

Business rules should remain stable.

---

# ADR-003

## Controllers Are Thin

Status

Accepted

Controller responsibilities

- receive UI requests
- validate UI input
- convert data
- call services

Controllers never

- contain business rules
- communicate with Google
- use Selenium
- access browser

---

# ADR-004

## Services Coordinate Workflows

Status

Accepted

Services

- validate domain rules
- coordinate providers
- produce domain results

Services never

- open browsers
- parse HTML
- read Excel

---

# ADR-005

## Providers Are Adapters

Status

Accepted

Providers convert

Application

↓

External Engine

Nothing else.

Providers never contain business decisions.

---

# ADR-006

## Engines Own External Communication

Status

Accepted

Engines

- Selenium
- Playwright
- Google Maps

All external communication belongs here.

---

# ADR-007

## Validation Fails Fast

Status

Accepted

Validation occurs before external calls.

Example

validate()

↓

provider.calculate()

Never call external systems with invalid input.

---

# ADR-008

## Unexpected Exceptions Propagate

Status

Accepted

Unexpected exceptions are not swallowed.

Reason

Hidden failures are harder to debug.

---

# ADR-009

## Domain Exceptions Become Domain Results

Status

Accepted

Known business exceptions become RouteResult.

Unexpected exceptions continue propagating.

---

# ADR-010

## Readability Over Cleverness

Status

Accepted

Readable code is preferred over compact code.

Developers should optimize for

- maintainability
- debugging
- onboarding

Not

- shortest code
- clever tricks

---

# ADR-011

## Avoid Micro Methods

Status

Accepted

Do not extract methods unless one of these is true

- reused
- isolates algorithm
- significantly improves readability

Do not extract because

- method exceeds arbitrary length
- style preference

---

# ADR-012

## Test Behavior

Status

Accepted

Tests verify observable behavior.

Avoid testing implementation details.

Private methods are tested only when they are intentionally pure algorithms.

---

# ADR-013

## Coverage Requirement

Status

Accepted

Minimum coverage

Statements

100%

Branches

100%

Reason

High confidence refactoring.

---

# ADR-014

## Explicit Dependencies

Status

Accepted

Every dependency appears in constructor.

Never retrieve hidden dependencies from globals.

---

# ADR-015

## Frozen Architecture

Status

Accepted

New features must respect existing architecture.

Architecture changes require discussion before implementation.