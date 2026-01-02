.PHONY: help install install-dev lint format type-check test test-cov clean run dev

PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package
	$(PYTHON) -m pip install -e .

install-dev:  ## Install package with dev dependencies
	$(PYTHON) -m pip install -e ".[dev]"
	pre-commit install

lint:  ## Run linter (ruff)
	$(BIN)/ruff check src tests
	$(BIN)/ruff format --check src tests

format:  ## Format code
	$(BIN)/ruff check --fix src tests
	$(BIN)/ruff format src tests

type-check:  ## Run type checker (mypy)
	$(BIN)/mypy src

test:  ## Run tests
	$(BIN)/pytest

test-cov:  ## Run tests with coverage
	$(BIN)/pytest --cov=src/daily_mcp --cov-report=term-missing --cov-report=html

check: lint type-check test  ## Run all checks (lint, type-check, test)

clean:  ## Clean build artifacts
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +

run:  ## Run the MCP server
	$(BIN)/daily-mcp

dev:  ## Run with debug logging
	DAILY_MCP_LOG_LEVEL=DEBUG $(BIN)/daily-mcp

venv:  ## Create virtual environment
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip

setup: venv  ## Setup development environment
	$(BIN)/pip install -e ".[dev]"
	$(BIN)/pre-commit install
	@echo "Setup complete! Activate venv with: source $(VENV)/bin/activate"
