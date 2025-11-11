# Makefile for Super Agents project

.PHONY: install test lint format docs clean format-markdown

# Install the package in development mode
install:
	pip install -e ".[dev]"

# Run tests
test:
	pytest

# Run linting
lint:
	ruff check super_agents/
	black --check super_agents/

# Format code
format:
	black super_agents/
	ruff check --fix super_agents/

# Format markdown files
format-markdown:
	find . -name "*.md" -exec python3 -m mdformat {} \;

# Build documentation
docs:
	# Documentation is in the docs/ directory as markdown files
	@echo "Documentation is available in the docs/ directory"

# Clean temporary files
clean:
	rm -rf .pytest_cache .ruff_cache __pycache__ super_agents/__pycache__
	rm -rf *.egg-info

# Run all checks
check: lint test

# Setup development environment
dev-setup:
	pip install -e ".[dev]"
	pre-commit install