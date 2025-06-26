# EcoFlow Cloud Integration Development Makefile
# Provides shortcuts for common development tasks

.PHONY: help reset docs run clean dev

# Default target
help:
	@echo "EcoFlow Cloud Integration Development Commands:"
	@echo ""
	@echo "Setup & Environment:"
	@echo "  reset         - Reset Home Assistant configuration"
	@echo ""
	@echo "Development:"
	@echo "  docs          - Generate device documentation"
	@echo "  run           - Run Home Assistant Core"
	@echo "  dev           - Setup development environment (reset + docs)"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean         - Clean up generated files"
	@echo "  update-readme - Reminder to update README with generated docs"

# Setup & Environment
reset:
	@echo "Updating Home Assistant core to latest..."
	cd core && git pull origin dev
	@echo "Resetting Home Assistant configuration..."
	rm -Rf ./core/config/
	mkdir ./core/config/
	ln -s $(PWD)/custom_components ./core/config/custom_components

# Development
docs:
	@echo "Generating device documentation..."
	cd docs && PYTHONPATH=$(PWD):$$PYTHONPATH python gen.py

run: reset
	@echo "Starting Home Assistant Core..."
	cd core && hass -c ./config

# Development shortcuts
dev: reset docs
	@echo "Development environment ready!"
	@echo "You can now run 'make run' to start Home Assistant"

# Maintenance
clean:
	@echo "Cleaning up generated files in custom_components..."
	find ./custom_components -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find ./custom_components -name "*.pyc" -delete 2>/dev/null || true
	find ./custom_components -name "*.pyo" -delete 2>/dev/null || true

update-readme:
	@echo "Manual step required:"
	@echo "1. Run 'make docs' to generate documentation"
	@echo "2. Replace the 'Current state' section in README.md with content from docs/summary.md"