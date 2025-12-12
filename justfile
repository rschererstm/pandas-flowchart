# pandas-flowchart justfile
# Run with: just <recipe>

# Default recipe - show available commands
default:
    @just --list

# Install dependencies
install:
    uv pip install -e ".[dev]"

# Install with all optional dependencies
install-all:
    uv pip install -e ".[dev,png]"
    uv pip install matplotlib seaborn

# Run all checks
check: lint typecheck test

# Run linter (ruff)
lint:
    ruff check pandas_flow/ tests/ examples/

# Run linter and fix issues
lint-fix:
    ruff check --fix --unsafe-fixes pandas_flow/ tests/ examples/

# Run formatter check (ruff format)
format-check:
    ruff format --check pandas_flow/ tests/ examples/

# Run formatter
format:
    ruff format pandas_flow/ tests/ examples/

# Run type checker (mypy)
typecheck:
    mypy pandas_flow/

# Run tests
test:
    pytest tests/ -v

# Run tests with coverage
test-cov:
    pytest tests/ -v --cov=pandas_flow --cov-report=term-missing

# Run tests with coverage and generate HTML report
test-cov-html:
    pytest tests/ -v --cov=pandas_flow --cov-report=html
    @echo "Coverage report: htmlcov/index.html"

# Run a specific test file
test-file file:
    pytest {{file}} -v

# Run the basic example
example:
    python examples/basic_example.py

# Run the healthcare pipeline example
example-healthcare:
    python examples/healthcare_pipeline.py

# Run the main demo
demo:
    python main.py

# Clean build artifacts
clean:
    rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/
    rm -rf htmlcov/ .coverage
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Clean output files
clean-output:
    rm -rf output/ examples/output/

# Build package
build:
    python -m build

# Full CI pipeline
ci: format-check lint typecheck test

# Watch for changes and run tests (requires watchexec)
watch-test:
    watchexec -e py -- just test

# Show package version
version:
    @python -c "import pandas_flow; print(pandas_flow.__version__)"

# Generate flowchart from example
generate-example:
    python examples/basic_example.py
    @echo "Generated files in examples/output/"

