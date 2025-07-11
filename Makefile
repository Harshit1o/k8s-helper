# Makefile for k8s-helper development

.PHONY: help install install-dev test test-cov lint format check clean build upload docs examples

help:
	@echo "Available commands:"
	@echo "  install      - Install package"
	@echo "  install-dev  - Install package in development mode with dev dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  check        - Run all checks (lint, format, test)"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  upload       - Upload package to PyPI"
	@echo "  docs         - Generate documentation"
	@echo "  examples     - Run example scripts"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/

test-cov:
	pytest --cov=k8s_helper --cov-report=html --cov-report=term-missing tests/

lint:
	flake8 src/k8s_helper tests/
	mypy src/k8s_helper

format:
	black src/k8s_helper tests/

format-check:
	black --check src/k8s_helper tests/

check: format-check lint test

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf src/k8s_helper.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	python -m twine upload dist/*

docs:
	@echo "Documentation is available in README.md"
	@echo "Open README.md in your browser or markdown viewer"

examples:
	@echo "Running basic web app example..."
	python examples/basic_web_app.py
	@echo ""
	@echo "Running multi-tier app example..."
	python examples/multi_tier_app.py
	@echo ""
	@echo "Running cleanup script..."
	python examples/cleanup_script.py

# Development shortcuts
dev-setup: install-dev
	@echo "Development environment setup complete!"

dev-test: format lint test-cov
	@echo "Development testing complete!"

# CI/CD commands
ci-test: install-dev check
	@echo "CI testing complete!"

release-check: clean build
	@echo "Release check complete!"

# Quick development commands
quick-test:
	pytest tests/test_core.py -v

quick-lint:
	flake8 src/k8s_helper/core.py src/k8s_helper/utils.py

quick-format:
	black src/k8s_helper/core.py src/k8s_helper/utils.py

# Package info
info:
	@echo "k8s-helper - Kubernetes Helper Library"
	@echo "Version: $(shell python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"
	@echo "Author: $(shell python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["authors"][0]["name"])')"
	@echo "Python: $(shell python --version)"
	@echo "Pip: $(shell pip --version)"
