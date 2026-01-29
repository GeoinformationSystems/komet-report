# KOMET Report Makefile
# ====================
# Common targets for local development and CI automation

.PHONY: all run html clean install check help venv clean-venv update serve

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

# Run notebook and generate HTML (full update)
update: run html

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
	rm -f komet_report_data.json

# Clean all generated files including timeline (preserves venv)
clean-all: clean
	rm -f komet_timeline.json

# Remove virtual environment
clean-venv:
	rm -rf $(VENV)

# Full clean including virtual environment
distclean: clean-all clean-venv

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
	@echo "  make update     - Run notebook and generate HTML"
	@echo "  make check      - Verify notebook executes without errors"
	@echo "  make serve      - Start local HTTP server for preview"
	@echo "  make clean      - Remove generated HTML and report data"
	@echo "  make clean-all  - Remove all generated files including timeline"
	@echo "  make clean-venv - Remove virtual environment"
	@echo "  make distclean  - Remove everything (clean-all + clean-venv)"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Virtual environment: $(VENV)/"
	@echo "CI workflow uses: make update"
	@echo ""
	@echo "Cell tags used:"
	@echo "  - remove-cell: Cells completely removed from HTML export"
	@echo "  - code_shown: Code cells expanded by default (otherwise collapsed)"
