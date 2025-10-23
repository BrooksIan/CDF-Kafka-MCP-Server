# CDF Kafka MCP Server Makefile

.PHONY: build clean test run install deps help

# Variables
PACKAGE_NAME=cdf-kafka-mcp-server
VERSION=1.0.0
BUILD_DIR=build
PYTHON_VERSION=3.9

# Default target
all: install

# Install dependencies
deps:
	@echo "Installing dependencies..."
	pip install -e .

# Install development dependencies
deps-dev:
	@echo "Installing development dependencies..."
	pip install -e ".[dev]"

# Build the package
build: clean
	@echo "Building $(PACKAGE_NAME)..."
	@mkdir -p $(BUILD_DIR)
	python -m build --outdir $(BUILD_DIR)

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR)
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run tests
test:
	@echo "Running tests..."
	python -m pytest Testing/ -v

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	python -m pytest Testing/ -v --cov=cdf_kafka_mcp_server --cov-report=html --cov-report=term-missing

# Run the server
run:
	@echo "Running $(PACKAGE_NAME)..."
	python -m cdf_kafka_mcp_server

# Run with configuration file
run-config:
	@echo "Running $(PACKAGE_NAME) with config..."
	python -m cdf_kafka_mcp_server --config config/kafka_config.yaml

# Install the package
install: deps
	@echo "Installing $(PACKAGE_NAME)..."
	pip install -e .

# Format code
fmt:
	@echo "Formatting code..."
	black src/ Testing/
	isort src/ Testing/

# Lint code
lint:
	@echo "Linting code..."
	flake8 src/ Testing/
	mypy src/

# Run all checks
check: fmt lint test
	@echo "All checks passed!"

# Run with debug logging
debug:
	@echo "Running $(PACKAGE_NAME) with debug logging..."
	MCP_LOG_LEVEL=DEBUG python -m cdf_kafka_mcp_server

# Create release package
release: build
	@echo "Creating release package..."
	@mkdir -p $(BUILD_DIR)/release
	@cp $(BUILD_DIR)/*.whl $(BUILD_DIR)/release/
	@cp $(BUILD_DIR)/*.tar.gz $(BUILD_DIR)/release/
	@cp README.md $(BUILD_DIR)/release/
	@cp config/kafka_config.yaml $(BUILD_DIR)/release/
	@cp claude_desktop_config.json $(BUILD_DIR)/release/
	@cd $(BUILD_DIR)/release && tar -czf $(PACKAGE_NAME)-$(VERSION).tar.gz *
	@echo "Release package created: $(BUILD_DIR)/release/$(PACKAGE_NAME)-$(VERSION).tar.gz"

# Docker build
docker-build:
	@echo "Building Docker image..."
	docker build -t $(PACKAGE_NAME):$(VERSION) .
	docker tag $(PACKAGE_NAME):$(VERSION) $(PACKAGE_NAME):latest

# Docker run
docker-run: docker-build
	@echo "Running Docker container..."
	docker run --rm -it $(PACKAGE_NAME):latest

# Development setup
dev-setup: deps-dev
	@echo "Setting up development environment..."
	@if ! command -v pre-commit >/dev/null 2>&1; then \
		echo "Installing pre-commit..."; \
		pip install pre-commit; \
	fi
	pre-commit install

# Check Python version
check-python:
	@echo "Checking Python version..."
	@python --version | grep -q "Python $(PYTHON_VERSION)" || (echo "Python $(PYTHON_VERSION) is required" && exit 1)

# Run example
example:
	@echo "Running example usage..."
	./examples/example_usage.sh

# Help
help:
	@echo "Available targets:"
	@echo "  build        Build the package"
	@echo "  clean        Clean build artifacts"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage"
	@echo "  run          Run the server"
	@echo "  run-config   Run with configuration file"
	@echo "  deps         Install dependencies"
	@echo "  deps-dev     Install development dependencies"
	@echo "  install      Install the package"
	@echo "  fmt          Format code"
	@echo "  lint         Lint code"
	@echo "  check        Run all checks"
	@echo "  debug        Run with debug logging"
	@echo "  release      Create release package"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run Docker container"
	@echo "  dev-setup    Set up development environment"
	@echo "  check-python Check Python version"
	@echo "  example      Run example usage"
	@echo "  help         Show this help message"
