# KOMET Reports

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18479191.svg)](https://doi.org/10.5281/zenodo.18479191)

Data reports on open metadata status in public knowledge bases by the KOMET project (<https://projects.tib.eu/komet>) on citation metadata and geometadata for scholarly works.
This repository implements tracking of contributions to the open metadata commons from OJS-based journals using the structured citations feature (as of OJS 3.6, formerly the [citation manager plugin](https://github.com/TIBHannover/citationManager)) and the [geometadata plugin](https://github.com/TIBHannover/geoMetadata).

**Target platforms**: OpenCitations and Wikidata

**View the report**: <https://geoinformationsystems.github.io/komet-report/>

<div>
<a href="https://projects.tib.eu/komet/en/">
<img src="https://projects.tib.eu/fileadmin/data/komet/img/Logo_Komet_RZ.png" alt="Alt-Text" title="KOMET Logo" width="20%" align="middle">
</a>
</div>

## Method

### Overview

This evaluation tracks the contributions of the KOMET project to the open metadata commons.
The primary goal is to measure the impact of OJS features and plugins that enable journals to contribute citation and geospatial metadata to open knowledge bases.
Key questions are:

- How many citation relationships have KOMET contributions added to OpenCitations and Wikidata?
- What is the baseline citation coverage for partner journals in Wikidata?
- How does metadata coverage change over time as more journals adopt the plugins?

As the main uptake developments are likely to occure after the project funding phase, this project contains a computational notebook that collects and saves relevant indicators.
The notebook is executed automatically on a regular schedule.
The analysis uses a set of journals from KOMET's collaboration partners, but may be readily extended.
Future projects may then expand the analysis and use the collected historic data to improve and extend the software infrastructure for capturing citation and geospatial metadata.

### Data sources and indicators

| Source | API | Purpose | Rate Limits |
|--------|-----|---------|-------------|
| **OpenCitations** | GitHub Issues API | Track crowdsourced citation deposits | 60 req/h (unauthenticated) |
| **Wikidata** | SPARQL endpoint | Query scholarly article metadata, citations (P2860), journal relationships (P1433) | Soft limits, timeout-based |

The following indicators are saved in local JSON files for the two main data sources.

- **OpenCitations**
  - `opencitations.total_issues`: Total crowdsourcing issues in the repository
  - `opencitations.komet_issues`: Issues created via KOMET-developed software
  - `opencitations.komet_done`: Successfully processed KOMET contributions
  - `opencitations.komet_pending`: KOMET contributions awaiting processing
  - `opencitations.komet_invalid`: KOMET contributions marked as invalid
- **Wikidata**
  - `wikidata.p1343_scholarly_count`: Scholarly articles with "described by source" property (baseline reference)
  - `wikidata.komet_provenance_count`: Items with KOMET provenance
  - `wikidata.journals.{QID}.articles`: Article count per partner journal
  - `wikidata.journals.{QID}.citations_p2860`: Outgoing citations per partner journal

**Historical statistics** are stored in `komet_timeline.json` using a hierarchical format, grouping by source and storing a compact series of `{t, v}` (timestamp, value) pairs.
Metrics include descriptive names, descriptions, and units.
New entries are only added when values change.
Journal metadata is stored once per journal.

### Partner Journals

The evaluation focuses on 15 journals from 8 collaboration partners that have committed to testing KOMET plugins:

| Partner | Journals | Platforms |
|---------|----------|-----------|
| KIM Universität Konstanz | 1 | OJS 3.3 |
| WWU Münster | 2 | OJS 3.3 |
| Julius Kühn-Institut | 3 | OJS 3.3 (OpenAgrar) |
| heiJOURNALS Heidelberg | 6 | OJS 3.2 |
| Deutsches Archäologisches Institut | 1 | OJS 3.4 |
| JOSIS / TU Dresden | 1 | OJS 3.3 |
| ZHB Luzern | 2 | OJS 3.3 |

Each journal is identified by its Wikidata QID (where available) to enable precise SPARQL queries.
A 2022 baseline was established for comparison with current values.

### Limitations

1. **P1343 (described by source)**: Initial analysis showed only ~14 scholarly articles use this property in Wikidata, making it unsuitable for tracking KOMET contributions. The project shifted focus to OpenCitations as the primary platform.
2. **Wikidata query timeouts**: Some aggregate queries (e.g., total P2860 citation count) may timeout due to dataset size (~3.4M citation relationships).
3. **OpenCitations processing lag**: Crowdsourced deposits may take weeks to be processed and appear in the OpenCitations corpus.
4. **Partner journal coverage**: Not all partner journals have Wikidata entries; 7 additional journals are tracked but cannot yet be queried via SPARQL.

### Automation

The notebook is designed to run weekly via GitHub Actions CI:

1. Execute `komet_evaluation.ipynb` using `nbconvert`
2. Update `komet_timeline.json` only when metric values change
3. Generate HTML report to `docs/` for GitHub Pages hosting
4. Commit and push updated data files

In addition, an annual CI action at the last day of December creates a new release, which is automatically deposited on Zenodo (<https://doi.org/10.5281/zenodo.18479191>).

## Files

| File | Description |
|------|-------------|
| `komet_evaluation.ipynb` | Main analysis notebook |
| `komet_helpers.py` | Python helper functions for API queries |
| `komet_timeline.json` | Timestamped observations log |
| `komet_report_data.json` | Latest report snapshot |
| `docs/index.html` | HTML report for GitHub Pages, rendered from notebook |
| `docs/komert_report.pdf` | PDF report for Zenodo archival, rendered from notebook |
| `Makefile` | Build automation for local development and CI |
| `templates/collapsible/` | Custom nbconvert template for collapsible code cells |

## Related repositories

- **OPTIMETA Citations Plugin**: <https://github.com/TIBHannover/optimetaCitations>
- **OPTIMETA Geo Plugin**: <https://github.com/TIBHannover/optimetaGeo>
- **OPTIMETA Plugin Shared**: <https://github.com/TIBHannover/optimeta-plugin-shared>
- **OPTIMAP**: <https://optimap.science/>
- **OpenCitations Crowdsourcing**: <https://github.com/opencitations/crowdsourcing>

## Usage

### Prerequisites

- Python 3.11+ (with `venv` module)
- Make

### Quick start

```bash
# Create virtual environment and install dependencies
make install

# Run the evaluation notebook interactively
.venv/bin/jupyter notebook komet_evaluation.ipynb

# Or run helper module directly for quick test
.venv/bin/python komet_helpers.py
```

### Local development

The project uses a Makefile that automatically manages a local `.venv` virtual environment. Run `make help` to see all available targets:

```bash
make help        # Show available targets
make install     # Create venv and install Python dependencies
make run         # Execute notebook (updates timeline and report data)
make html        # Generate HTML report in docs/
make update      # Run notebook and generate HTML (full update)
make check       # Verify notebook executes without errors
make serve       # Start local HTTP server to preview docs/
make clean       # Remove generated HTML and report data
make clean-all   # Remove all generated files including timeline
make clean-venv  # Remove virtual environment
make distclean   # Remove everything (clean-all + clean-venv)
```

### Virtual environment

The Makefile automatically creates and uses a `.venv` directory for Python dependencies. This ensures:

- Reproducible builds locally and in CI
- No interference with system Python packages
- Easy cleanup with `make clean-venv`

To start fresh with a clean environment:

```bash
make distclean   # Remove all generated files and venv
make update      # Recreate venv, install deps, run notebook, generate HTML
```

### Generating the report locally

To regenerate the HTML report for preview:

```bash
# Full update: execute notebook and generate HTML
make update

# Preview the generated HTML locally
make serve
# Then open http://localhost:8000 in your browser
```

To generate a PDF report using [typst](https://typst.app/docs/guides/install/):

```bash
make pdf    # Generates docs/komet_report.pdf
```
The PDF is generated by converting the notebook to markdown via nbconvert, then compiling with typst using the cmarker package.
Code cells are excluded; only narrative and visualizations are included.

### Cell Tags

The notebook uses cell tags to control HTML export behavior:

| Tag | Effect |
|-----|--------|
| `remove-cell` | Cell completely removed from HTML export |
| `code_shown` | Code cell expanded by default (otherwise collapsed) |

Code cells without tags are collapsed but can be expanded by clicking "Show Code".

### CI Automation

The GitHub Actions workflow (`.github/workflows/update-report.yml`) automates report generation:

1. Install pandoc 3.x and typst for PDF generation
2. `make install` - Create venv and install Python dependencies
3. `make update` - Execute notebook and generate HTML
4. Check if data content changed (ignoring timestamp-only updates)
5. `make pdf` - Generate PDF report (only if data changed)
6. Commit and push all outputs (only if data changed)

**Change detection**: The workflow compares the report data excluding timestamps. This prevents unnecessary commits when the data sources return identical values but the report timestamp updates.

The workflow runs automatically on the 1st of each month at 06:00 UTC and can be triggered manually via the GitHub Actions UI.

### Releases

The CI workflow supports creating GitHub releases both automatically and manually.

**Automatic year-end release:**

- Runs on December 31st at 23:00 UTC
- Creates release with tag `vYYYY` (e.g., `v2025`)
- Includes `komet_report.pdf` and `index.html` as assets

**Manual release (for first release or out-of-schedule releases):**

1. Go to **Actions** → **Update KOMET Report**
2. Click **Run workflow**
3. Check **Create a GitHub release**
4. Optionally set a custom **Release tag** (e.g., `v2024`, `v2025.1`, `v2025-interim`)
   - Leave empty for auto-generated `vYYYY` tag
   - If the tag already exists, `.1`, `.2`, etc. is appended automatically
5. Click **Run workflow**

**Release assets:**

- `komet_report.pdf` - PDF version of the evaluation report
- `index.html` - Interactive HTML version (also available via GitHub Pages)

## Citation

If you use this dataset or software, please cite it as:

> Nüst, D., Niers, T., Hauschke, C., & Yücel, G. (2026). *KOMET Project - Open Metadata Evaluation Report* [Data set]. Zenodo. <https://doi.org/10.5281/zenodo.18479191>

```bibtex
@dataset{komet_report_2026,
  author       = {Nüst, Daniel and Niers, Tom and Hauschke, Christian and Yücel, Gazi},
  title        = {{KOMET Project - Open Metadata Evaluation Report}},
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.18479191},
  url          = {https://doi.org/10.5281/zenodo.18479191}
}
```

## Funding

This work is funded by the German Federal Ministry of Education and Research (BMBF) under grant number `16TOA039`.

[![BMBF Logo](https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/BMBF_Logo.svg/320px-BMBF_Logo.svg.png)](https://www.bmbf.de/)

The KOMET project (Förderkennzeichen 16TOA039) is part of the funding initiative "Förderung von Projekten zur Etablierung einer gelebten Open-Access-Kultur in der deutschen Forschungs- und Wissenschaftspraxis."

## License

**Code**: CC0-1.0

**Report outputs**: CC-BY-4.0

### External Data Sources

This project uses data from the following sources:

| Source | License | Link |
|--------|---------|------|
| Wikidata | CC0 1.0 | <https://www.wikidata.org/wiki/Wikidata:Licensing> |
| OpenCitations | CC0 1.0 | <https://opencitations.net/about#licensing> |
