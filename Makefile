# Colors for prettier output
GREEN := \033[0;32m
NC := \033[0m # No Color

.PHONY: help build install install-dev test lint format clean clean-unix clean-windows

help: ## Display this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk -F ':|##' '/^[^\t].+?:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$NF }' $(MAKEFILE_LIST)

build: clean ## Build the application
	uv build --wheel

install:  ## Install all dependencies
	uv pip install . --link-mode=copy

dev:  build ## Install development dependencies
	uv pip install -U -e ".[dev]"

test:  ## Run all tests
	pytest -v tests/

lint: ## Code linting
	flake8 src/ tests/ --ignore=E501
	black --check src/ tests/
	isort --check-only src/ tests/

format: ## Code formatting
	black src/ tests/
	isort src/ tests/

clean: ## Clean up temporary files (auto-detects OS)
ifeq ($(OS),Windows_NT)
	$(MAKE) clean-windows
else
	$(MAKE) clean-unix
endif

clean-unix: ## Clean up temporary files (Unix)
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +

clean-windows: ## Clean up temporary files (Windows)
	if exist "__pycache__" rd /s /q "__pycache__"
	if exist ".pytest_cache" rd /s /q ".pytest_cache"
	if exist ".coverage" del /f /q ".coverage"
	if exist "dist" rd /s /q "dist"
	if exist "build" rd /s /q "build"
	if exist "*.egg-info" rd /s /q "*.egg-info"
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
	for /d /r . %%d in (*.egg-info) do @if exist "%%d" rd /s /q "%%d"
