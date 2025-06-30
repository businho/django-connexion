.PHONY: help install install-dev test test-cov lint format check clean build docs

# Default target
help:
	@echo "Available commands:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests without coverage"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black and isort"
	@echo "  check        Run all checks (lint + test)"
	@echo "  clean        Clean build artifacts and cache"
	@echo "  build        Build package"
	@echo "  docs         Generate documentation"

# Installation commands
install:
	pip install -e .

install-dev: install
	pip install -r requirements-dev.txt

# Testing commands
test: lint
	python -m pytest --no-cov -v

test-cov: lint
	python -m pytest

# Code quality commands
lint:
	black --check django_connexion/
	isort --check-only django_connexion/
	flake8 django_connexion/
	mypy django_connexion/ --ignore-missing-imports

format:
	black django_connexion/
	isort django_connexion/

check: format lint test

# Cleanup commands
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build commands
build: clean
	python -m build

# Documentation (placeholder for future use)
docs:
	@echo "Documentation generation not yet configured"
