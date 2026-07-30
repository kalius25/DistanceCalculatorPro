# Coding Guidelines

Version 1.0

---

# Naming

Classes

PascalCase

Methods

snake_case

Variables

snake_case

Constants

UPPER_CASE

---

# Type Hints

Always required.

Good

def calculate(
    request: RouteRequest
) -> RouteResult:

Bad

def calculate(request):

---

# Constructor Injection

Always inject.

Good

class Service:

    def __init__(
        self,
        provider
    ):

Bad

class Service:

    def calculate(self):

        provider = GoogleProvider()

---

# Private Fields

Dependencies start with "_".

self._provider

self._engine

---

# Properties

Expose compatibility only.

@property

def provider(...)

No business logic inside properties.

---

# Functions

Prefer readable workflows.

Avoid tiny helper methods.

Extract methods ONLY when

- reused
- significantly reduce complexity
- improve readability

Do NOT extract because

- "method too long"
- "style preference"

---

# Exceptions

Raise domain exceptions.

Never return None.

Never swallow unexpected exceptions.

---

# Logging

Log business events.

Do not log every private method.

---

# Comments

Explain WHY.

Not WHAT.

Bad

# Increment index

index += 1

Good

# Skip header row

---

# Imports

Standard

↓

Third-party

↓

Project

---

# Maximum Nesting

Target ≤ 3

Prefer early return.

---

# Dataclasses

Prefer

@dataclass(
    frozen=True,
    slots=True
)

for immutable models.
