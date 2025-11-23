.PHONY: help install install-dev clean lint format test coverage docs serve-docs setup pre-commit

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PROJECT_DIR := project_data_science
SRC_DIR := $(PROJECT_DIR)/src
TESTS_DIR := $(PROJECT_DIR)/tests
NOTEBOOKS_DIR := $(PROJECT_DIR)/notebooks

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install project dependencies
	cd $(PROJECT_DIR) && $(PIP) install -e .

install-dev: ## Install development dependencies
	cd $(PROJECT_DIR) && $(PIP) install -e ".[dev,docs]"
	pre-commit install

clean: ## Clean temporary files and caches
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

lint: ## Run code linting (ruff check)
	cd $(PROJECT_DIR) && ruff check $(SRC_DIR) $(TESTS_DIR)

format: ## Format code with ruff
	cd $(PROJECT_DIR) && ruff format $(SRC_DIR) $(TESTS_DIR)
	cd $(PROJECT_DIR) && ruff check --fix $(SRC_DIR) $(TESTS_DIR)

type-check: ## Run static type checking with mypy
	cd $(PROJECT_DIR) && mypy $(SRC_DIR)

test: ## Run tests with pytest
	cd $(PROJECT_DIR) && pytest $(TESTS_DIR) -v

test-cov: ## Run tests with coverage report
	cd $(PROJECT_DIR) && pytest $(TESTS_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term

coverage: test-cov ## Alias for test-cov

docs: ## Build documentation
	cd $(PROJECT_DIR) && mkdocs build

serve-docs: ## Serve documentation locally
	cd $(PROJECT_DIR) && mkdocs serve

setup: install-dev ## Complete setup (install deps + pre-commit)
	@echo "✅ Setup complete! Run 'make help' to see available commands."

pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

notebook-clean: ## Strip output from all notebooks
	nbstripout $(NOTEBOOKS_DIR)/**/*.ipynb

# Data Engineering commands
airflow-init: ## Initialize Airflow database
	cd project_data_engineer && airflow db init

airflow-start: ## Start Airflow webserver and scheduler
	cd project_data_engineer && airflow webserver -D && airflow scheduler -D

airflow-stop: ## Stop Airflow services
	pkill -f "airflow webserver" || true
	pkill -f "airflow scheduler" || true

# Streamlit apps
app-facas: ## Run Streamlit app for facas analysis
	cd $(PROJECT_DIR)/src && streamlit run app.py

# Docker commands (if needed in the future)
docker-build: ## Build Docker image
	docker build -t case_embalagens:latest .

docker-run: ## Run Docker container
	docker run -p 8501:8501 case_embalagens:latest
