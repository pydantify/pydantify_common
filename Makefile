PROJECT=pydantify_common
CODE_DIRS=src/${PROJECT} tests

# Run pytest
.PHONY: pytest
pytest:
	uv run pytest -vs ${ARGS}

# Check if the python code needs to be reformatted
.PHONY: ruff
black:
	uv run ruff format --check ${CODE_DIRS}

# Python type check
.PHONY: mypy
mypy:
	uv run mypy src/${PROJECT}

# Runn pytest, black and mypy
.PHONY: tests
tests: pytest black mypy
