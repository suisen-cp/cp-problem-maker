.PHONY: fix-lint
fix-lint:
	poetry run ruff check --fix src tests

.PHONY: fmt
fmt:
	poetry run ruff format src tests

.PHONY: check
check: check-ruff-lint check-mypy-type

.PHONY: check-ruff-lint
check-ruff-lint:
	poetry run ruff check src tests

.PHONY: check-mypy-type
check-mypy-type:
	poetry run mypy --install-types --non-interactive src tests

.PHONY: tests
tests:
	poetry run pytest tests
