# DistanceCalculatorPro Architecture

Version: 1.0
Status: Architecture Frozen

---

# 1. Goals

This project follows:

- Dependency Injection
- SOLID
- Explicit dependencies
- High testability
- Low coupling
- High readability

Business logic must not create infrastructure objects.

---

# 2. Layer Architecture

UI

↓

Controller

↓

Application Service

↓

Provider

↓

Engine

↓

External System

---

# 3. Responsibilities

## Controller

Responsibilities

- Receive UI requests
- Validate UI input
- Read/write Excel
- Build domain requests

Must NOT

- Create Providers
- Create Engines
- Perform route calculations

---

## Application Service

Responsibilities

- Coordinate workflow
- Validate business rules
- Log business events
- Call Provider

Must NOT

- Know browser implementation
- Know Google Maps implementation
- Read Excel

---

## Provider

Responsibilities

- Adapt one external provider
- Call Engine

Must NOT

- Create Browser
- Create Engine
- Coordinate workflows

---

## Engine

Responsibilities

- Communicate with external systems

Must NOT

- Perform business decisions

---

# 4. Dependency Flow

Allowed

Controller
    ↓
Service
    ↓
Provider
    ↓
Engine

Forbidden

Controller → Engine

Controller → Browser

Service → Browser

Service → Google Maps

Provider → Excel

Engine → Excel

---

# 5. Dependency Injection

All dependencies are constructor injected.

Example

class CalculationService:

    def __init__(
        self,
        provider: BaseProvider
    ):
        self._provider = provider

Never instantiate dependencies inside business classes.

Wrong

self.provider = GoogleProvider()

Correct

Provider is injected.

---

# 6. Configuration

Configuration objects are immutable.

Configuration is loaded once.

No global mutable state.

---

# 7. Logging

Business events are logged.

Infrastructure logs remain inside engines.

---

# 8. Exception Rules

ValidationException

↓

Application

↓

Caller

Unexpected exceptions

↓

Propagate

No silent failures.

---

# 9. Testing

Every layer has isolated unit tests.

No network.

No browser.

No Google Maps.

Use mocks only.

Coverage target

100%
