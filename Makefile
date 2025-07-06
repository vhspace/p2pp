# P2PP Development Makefile
# Uses uv for fast package management and pytest for testing

.PHONY: help install install-dev test test-unit test-integration test-e2e test-platform test-coverage clean build lint format check-arch test-arch setup-uv

# Default target
help:
	@echo "P2PP Development Commands (using uv and pytest)"
	@echo "================================================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup-uv          Install uv if not available"
	@echo "  install           Install project dependencies"
	@echo "  install-dev       Install with development dependencies"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test              Run all tests"
	@echo "  test-unit         Run unit tests only"
	@echo "  test-integration  Run integration tests only"
	@echo "  test-e2e          Run end-to-end tests only"
	@echo "  test-platform     Run platform-specific tests"
	@echo "  test-coverage     Run tests with coverage report"
	@echo "  test-arch         Test architecture-specific builds"
	@echo ""
	@echo "Build Commands:"
	@echo "  build             Build for current platform"
	@echo "  build-intel       Build for Intel (macOS only)"
	@echo "  build-arm         Build for ARM (macOS only)"
	@echo "  clean             Clean build artifacts"
	@echo ""
	@echo "Quality Commands:"
	@echo "  lint              Run linting (flake8, mypy)"
	@echo "  format            Format code (black, isort)"
	@echo "  check-arch        Check system architecture"
	@echo ""
	@echo "Architecture Detection:"
	@echo "  Platform: $(shell python3 -c 'import platform; print(platform.system())')"
	@echo "  Machine:  $(shell python3 -c 'import platform; print(platform.machine())')"

# Detect platform for conditional commands
PLATFORM := $(shell python3 -c 'import platform; print(platform.system())')
MACHINE := $(shell python3 -c 'import platform; print(platform.machine())')

# Setup Commands
setup-uv:
	@echo "Installing uv..."
	@which uv > /dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
	@echo "uv installed successfully"

install: setup-uv
	@echo "Installing project dependencies..."
	uv pip install -e .
	@echo "Dependencies installed"

install-dev: setup-uv
	@echo "Installing development dependencies..."
	uv pip install -e ".[dev]"
ifeq ($(PLATFORM),Darwin)
	uv pip install -e ".[test-macos,build-macos]"
else ifeq ($(PLATFORM),Windows)
	uv pip install -e ".[test-windows,build-windows]"
else ifeq ($(PLATFORM),Linux)
	uv pip install -e ".[test-linux,build-linux]"
endif
	@echo "Development dependencies installed"

# Testing Commands
test: install-dev
	@echo "Running all tests..."
	python3 -m pytest -v --tb=short

test-unit: install-dev
	@echo "Running unit tests..."
	python3 -m pytest tests/unit/ -v -m unit

test-integration: install-dev
	@echo "Running integration tests..."
	python3 -m pytest tests/integration/ -v -m integration

test-e2e: install-dev
	@echo "Running end-to-end tests..."
	python3 -m pytest tests/e2e/ -v -m e2e

test-platform: install-dev
	@echo "Running platform-specific tests for $(PLATFORM)..."
ifeq ($(PLATFORM),Darwin)
	python3 -m pytest -v -m macos
else ifeq ($(PLATFORM),Windows)
	python3 -m pytest -v -m windows
else ifeq ($(PLATFORM),Linux)
	python3 -m pytest -v -m linux
endif

test-coverage: install-dev
	@echo "Running tests with coverage..."
	python3 -m pytest --cov=p2pp --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/"

test-arch: install-dev
	@echo "Testing architecture-specific builds..."
	python3 scripts/test_architecture_builds.py

# Build Commands
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

build: clean install
	@echo "Building for $(PLATFORM) $(MACHINE)..."
ifeq ($(PLATFORM),Darwin)
	@$(MAKE) build-native-macos
else ifeq ($(PLATFORM),Windows)
	python3 setup.py bdist_msi
else ifeq ($(PLATFORM),Linux)
	python3 setup.py bdist_rpm
endif
	@echo "Build complete. Check dist/ directory."

build-native-macos:
ifeq ($(MACHINE),x86_64)
	@$(MAKE) build-intel
else ifeq ($(MACHINE),arm64)
	@$(MAKE) build-arm
else
	@echo "Unknown macOS architecture: $(MACHINE)"
	@exit 1
endif

build-intel:
ifeq ($(PLATFORM),Darwin)
	@echo "Building Intel binary..."
	export ARCHFLAGS="-arch x86_64" && python3 setup.py py2app --arch=x86_64
else
	@echo "Intel builds are only supported on macOS"
	@exit 1
endif

build-arm:
ifeq ($(PLATFORM),Darwin)
	@echo "Building ARM binary..."
	export ARCHFLAGS="-arch arm64" && python3 setup.py py2app --arch=arm64
else
	@echo "ARM builds are only supported on macOS"
	@exit 1
endif

# Quality Commands
lint: install-dev
	@echo "Running linting..."
	python3 -m flake8 p2pp/ tests/ scripts/
	python3 -m mypy p2pp/ --ignore-missing-imports

format: install-dev
	@echo "Formatting code..."
	python3 -m black p2pp/ tests/ scripts/
	python3 -m isort p2pp/ tests/ scripts/

check-arch:
	@echo "Checking system architecture..."
	python3 scripts/check_architecture.py

# Development Helpers
dev-setup: install-dev
	@echo "Setting up development environment..."
	pre-commit install || echo "pre-commit not available, skipping hooks"
	@echo "Development environment ready!"

# CI Commands (for GitHub Actions)
ci-test: install-dev
	@echo "Running CI tests..."
	python3 -m pytest -v --tb=short --junitxml=test-results.xml

ci-build: clean install
	@echo "Running CI build..."
	@$(MAKE) build

# Quick commands for common workflows
quick-test:
	python3 -m pytest tests/unit/ -v --tb=line -x

watch-test: install-dev
	@echo "Watching for changes and running tests..."
	python3 -m pytest tests/unit/ -v --tb=line -f

# Help for specific commands
help-testing:
	@echo "Testing Commands Help:"
	@echo "====================="
	@echo ""
	@echo "test          - Run all tests (unit + integration + e2e)"
	@echo "test-unit     - Fast unit tests for core functionality"
	@echo "test-integration - Integration tests for build system"
	@echo "test-e2e      - End-to-end tests for complete workflows"
	@echo "test-platform - Tests specific to current platform"
	@echo "test-coverage - Generate coverage report"
	@echo "test-arch     - Test architecture detection and builds"
	@echo ""
	@echo "Test Markers:"
	@echo "  -m unit          Unit tests only"
	@echo "  -m integration   Integration tests only"
	@echo "  -m e2e           End-to-end tests only"
	@echo "  -m gui           GUI tests (skipped in CI)"
	@echo "  -m slow          Slow tests"
	@echo "  -m macos         macOS-specific tests"
	@echo "  -m windows       Windows-specific tests"
	@echo "  -m linux         Linux-specific tests"

help-building:
	@echo "Building Commands Help:"
	@echo "======================"
	@echo ""
	@echo "build        - Build for current platform/architecture"
	@echo "build-intel  - Build Intel x86_64 (macOS only)"
	@echo "build-arm    - Build ARM64 (macOS only)"
	@echo "clean        - Remove all build artifacts"
	@echo ""
	@echo "Platform Detection:"
	@echo "  Current platform: $(PLATFORM)"
	@echo "  Current machine:  $(MACHINE)"
	@echo ""
	@echo "Output Locations:"
	@echo "  macOS: dist/P2PP.app, dist/P2PP-{intel,arm}.dmg"
	@echo "  Windows: dist/P2PP.msi"
	@echo "  Linux: dist/p2pp-*.rpm, dist/deb/p2pp*.deb"