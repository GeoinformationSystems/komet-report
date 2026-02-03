# KOMET Report Makefile
# ====================
# Common targets for local development and CI automation

.PHONY: all run html pdf clean install check help venv clean-venv update serve

# Virtual environment directory
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
JUPYTER := $(VENV)/bin/jupyter

# Default target
all: run html

# Create virtual environment
venv: $(VENV)/bin/activate

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

# Install Python dependencies into virtual environment
install: venv
	$(PIP) install -r requirements.txt

# Run the notebook (execute all cells, update in place)
run: install
	$(JUPYTER) nbconvert \
		--to notebook \
		--execute \
		--inplace \
		komet_evaluation.ipynb

# Generate HTML report for GitHub Pages
# - Removes cells tagged with "remove-cell"
# - Code cells collapsed by default (expandable via toggle)
# - Cells tagged with "code_shown" are expanded by default
# - Updates HTML title for better display
html: install
	$(JUPYTER) nbconvert \
		--to html \
		--template=templates/collapsible \
		--output-dir=docs \
		--output=index \
		--TagRemovePreprocessor.enabled=True \
		--TagRemovePreprocessor.remove_cell_tags='["remove-cell"]' \
		--HTMLExporter.anchor_link_text=' ' \
		--TemplateExporter.exclude_input_prompt=True \
		komet_evaluation.ipynb
	@echo "HTML report generated: docs/index.html"
	@# Update the HTML title tag for better browser display
	@sed -i 's|<title>komet_evaluation</title>|<title>KOMET Project - Open Metadata Evaluation Report</title>|g' docs/index.html

# Generate PDF report using typst
# Requires: typst installed on system
# Note: Run 'make run' first to execute the notebook
pdf: install
	@if ! command -v typst >/dev/null 2>&1; then \
		echo "Error: typst not found. Install from https://typst.app/docs/guides/install/"; \
		exit 1; \
	fi
	$(JUPYTER) nbconvert \
		--to markdown \
		--output-dir=docs \
		--output=report \
		--no-input \
		--no-prompt \
		--TagRemovePreprocessor.enabled=True \
		--TagRemovePreprocessor.remove_cell_tags='["remove-cell"]' \
		komet_evaluation.ipynb
	@# Download external images and replace URLs with local paths
	@mkdir -p docs/images
	@cd docs && for url in $$(grep -oE 'https://[^)]+\.(png|jpg|svg)' report.md | head -20); do \
		filename=$$(echo "$$url" | sed 's|.*/||; s|%20|_|g'); \
		echo "Downloading $$filename from $$url..."; \
		wget -q --timeout=10 "$$url" -O "images/$$filename" 2>/dev/null; \
		if [ -s "images/$$filename" ]; then \
			sed -i "s|$$url|images/$$filename|g" report.md; \
		else \
			echo "  Warning: Download failed or empty, removing image reference"; \
			rm -f "images/$$filename"; \
			sed -i "s|!\[[^]]*\]($$url)||g" report.md; \
		fi; \
	done
	cp templates/komet_report.typ docs/komet_report.typ
	cd docs && typst compile --root . komet_report.typ komet_report.pdf
	rm -f docs/report.md docs/komet_report.typ
	rm -rf docs/report_files docs/images
	@echo "PDF report generated: docs/komet_report.pdf"

# Run notebook and generate HTML and PDF (full update)
update: run html pdf

# Check if notebook can execute without errors (dry run)
check: install
	$(JUPYTER) nbconvert \
		--to notebook \
		--execute \
		--stdout \
		komet_evaluation.ipynb > /dev/null

# Clean generated files (preserves timeline data and venv)
clean:
	rm -f docs/index.html
	rm -f docs/komet_report.pdf
	rm -f komet_report_data.json

# Remove virtual environment
clean-venv:
	rm -rf $(VENV)

# Serve docs locally for preview
serve: install
	@echo "Starting local server at http://localhost:8000"
	@cd docs && $(PYTHON) -m http.server 8000

# Show help
help:
	@echo "KOMET Report - Available targets:"
	@echo ""
	@echo "  make install    - Create venv and install Python dependencies"
	@echo "  make run        - Execute notebook (updates data files)"
	@echo "  make html       - Generate HTML report in docs/"
	@echo "  make pdf        - Generate PDF report using typst (requires typst CLI)"
	@echo "  make update     - Run notebook and generate HTML and PDF"
	@echo "  make check      - Verify notebook executes without errors"
	@echo "  make serve      - Start local HTTP server for preview"
	@echo "  make clean      - Remove generated HTML and report data"
	@echo "  make clean-venv - Remove virtual environment"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Virtual environment: $(VENV)/"
	@echo "CI workflow uses: make update"
	@echo ""
	@echo "Cell tags used:"
	@echo "  - remove-cell: Cells completely removed from HTML export"
	@echo "  - code_shown: Code cells expanded by default (otherwise collapsed)"
