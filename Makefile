# AI Content Generation Suite Makefile

.PHONY: install install-dev install-deps test-all build-all clean format lint \
        release-patch release-minor release-major release-check version

# Install dependencies and all packages
install: install-deps install-dev

# Install dependencies from root requirements.txt
install-deps:
	@echo "📦 Installing dependencies from requirements.txt..."
	pip install -r requirements.txt

# Install all packages in development mode
install-dev:
	@echo "🔧 Installing all packages in development mode..."
	@find packages -name "setup.py" -exec dirname {} \; | while read dir; do \
		echo "Installing $$dir..."; \
		pip install -e $$dir; \
	done

# Run tests for all packages
test-all:
	@echo "🧪 Running tests for all packages..."
	@find packages -name "tests" -type d | while read testdir; do \
		echo "Testing $$testdir..."; \
		cd "$$(dirname $$testdir)" && python -m pytest tests/; \
	done

# Build all packages
build-all:
	@echo "📦 Building all packages..."
	@find packages -name "setup.py" -exec dirname {} \; | while read dir; do \
		echo "Building $$dir..."; \
		cd $$dir && python -m build; \
	done

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true

# Format code
format:
	@echo "🎨 Formatting code..."
	@black packages/
	@isort packages/

# Lint code
lint:
	@echo "🔍 Linting code..."
	@flake8 packages/
	@black --check packages/
	@isort --check-only packages/

# Show current version
version:
	@grep -m1 'VERSION = ' setup.py | cut -d'"' -f2

# Check version consistency across all files
release-check:
	@echo "🔍 Checking version consistency..."
	@SETUP_VER=$$(grep -m1 'VERSION = ' setup.py | cut -d'"' -f2); \
	PIPE_VER=$$(grep -m1 '__version__ = ' packages/core/ai_content_pipeline/ai_content_pipeline/__init__.py | cut -d'"' -f2); \
	PLAT_VER=$$(grep -m1 '__version__ = ' packages/core/ai_content_platform/__version__.py | cut -d'"' -f2); \
	echo "  setup.py:              $$SETUP_VER"; \
	echo "  ai_content_pipeline:   $$PIPE_VER"; \
	echo "  ai_content_platform:   $$PLAT_VER"; \
	if [ "$$SETUP_VER" = "$$PIPE_VER" ] && [ "$$SETUP_VER" = "$$PLAT_VER" ]; then \
		echo "✅ All versions match: $$SETUP_VER"; \
	else \
		echo "❌ Version mismatch detected!"; \
		exit 1; \
	fi

# Release: bump patch version (1.0.18 -> 1.0.19)
release-patch: release-check
	@echo "🚀 Releasing patch version..."
	bump2version patch
	git push origin HEAD --tags
	@echo "✅ Patch release complete! Create GitHub release to trigger PyPI publish."

# Release: bump minor version (1.0.18 -> 1.1.0)
release-minor: release-check
	@echo "🚀 Releasing minor version..."
	bump2version minor
	git push origin HEAD --tags
	@echo "✅ Minor release complete! Create GitHub release to trigger PyPI publish."

# Release: bump major version (1.0.18 -> 2.0.0)
release-major: release-check
	@echo "🚀 Releasing major version..."
	bump2version major
	git push origin HEAD --tags
	@echo "✅ Major release complete! Create GitHub release to trigger PyPI publish."
