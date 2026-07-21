ruff check .
mypy app
pytest
pytest --cov=app --cov-report=term-missing
coverage html