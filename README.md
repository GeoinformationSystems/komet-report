# KOMET Reports

Data reports on open metadata status in public knowledge bases by the KOMET project (<https://projects.tib.eu/komet>) on citation metadata and geometadata for scholarly works.
This repository implements tracking of contributions to the open metadata commons from OJS-based journals using the structured citations feature (as of OJS 3.6, formerly the [citation manager plugin](https://github.com/TIBHannover/citationManager)) and the [geometadata plugin](https://github.com/TIBHannover/geoMetadata).

**Target platforms**: OpenCitations and Wikidata

## Methodology

### Goals

This evaluation tracks the contributions of the KOMET project to the open metadata commons.
The primary goal is to measure the impact of OJS features and plugins that enable journals to contribute citation and geospatial metadata to open knowledge bases.

**Key questions:**

- How many citation relationships have KOMET contributions added to OpenCitations and Wikidata?
- What is the baseline citation coverage for partner journals in Wikidata?
- How does metadata coverage change over time as more journals adopt the plugins?

### Data Sources

| Source | API | Purpose | Rate Limits |
|--------|-----|---------|-------------|
| **OpenCitations** | GitHub Issues API | Track crowdsourced citation deposits | 60 req/h (unauthenticated) |
| **Wikidata** | SPARQL endpoint | Query scholarly article metadata, citations (P2860), journal relationships (P1433) | Soft limits, timeout-based |
| **OpenAlex** | REST API | Planned: comprehensive metadata completeness analysis | 100k req/day |
| **OPTIMAP** | TBD | Planned: geospatial metadata tracking | TBD |

### Metrics Collected

**OpenCitations**

- `opencitations.total_issues`: Total crowdsourcing issues in the repository
- `opencitations.komet_issues`: Issues created via KOMET-developed software
- `opencitations.komet_done`: Successfully processed KOMET contributions
- `opencitations.komet_pending`: KOMET contributions awaiting processing
- `opencitations.komet_invalid`: KOMET contributions marked as invalid

**Wikidata**

- `wikidata.p1343_scholarly_count`: Scholarly articles with "described by source" property (baseline reference)
- `wikidata.komet_provenance_count`: Items with KOMET provenance
- `wikidata.journals.{QID}.articles`: Article count per partner journal
- `wikidata.journals.{QID}.citations_p2860`: Outgoing citations per partner journal

### Partner Journals

The evaluation tracks 15 journals from 8 collaboration partners that have committed to testing KOMET plugins:

| Partner | Journals | Platforms |
|---------|----------|-----------|
| KIM Universität Konstanz | 1 | OJS 3.3 |
| WWU Münster | 2 | OJS 3.3 |
| Julius Kühn-Institut | 3 | OJS 3.3 (OpenAgrar) |
| heiJOURNALS Heidelberg | 6 | OJS 3.2 |
| Deutsches Archäologisches Institut | 1 | OJS 3.4 |
| JOSIS / TU Dresden | 1 | OJS 3.3 |
| ZHB Luzern | 2 | OJS 3.3 |

Each journal is identified by its Wikidata QID (where available) to enable precise SPARQL queries. A 2022 baseline was established for comparison with current values.

### Timeline Tracking

Statistics are stored in `komet_timeline.json` using a hierarchical v2.0 format:

1. **Structured metrics**: Metrics are grouped by source (wikidata, opencitations) with metadata
2. **Time series**: Each metric stores a compact series of `{t, v}` (timestamp, value) pairs
3. **Change detection**: New entries are only added when values change
4. **Human-readable**: Metrics include descriptive names, descriptions, and units
5. **Reduced duplication**: Journal metadata is stored once per journal, not repeated per observation

Example structure:

```json
{
  "metrics": {
    "wikidata": {
      "journals": {
        "Q123456": {
          "name": "Journal Name",
          "partner": "Institution",
          "articles": { "series": [{"t": "2026-01-22T12:00:00Z", "v": 42}] }
        }
      }
    }
  }
}
```

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

## Tasks

### Data Collection (Primary)

- [x] Collect metadata from OpenCitations repository issues
- [x] Query Wikidata scholarly graph for citations (P2860), filtered by partner journals
- [ ] Explore OpenAIRE for citations, e.g., based on a curated list of journals
- [ ] Query OpenAlex for partner journal metadata completeness

### Data Collection (Secondary)

- [x] Analyse Wikidata P1343 usage for scholarly articles (finding: limited reach, ~14 items)
- [x] Query Wikidata scholarly graph for research works with geometadata (baseline)
- [ ] Query OPTIMAP for publications with spatial metadata

### Statistics & Analysis

- [x] Create baseline statistics for partner journals in Wikidata
- [x] Track OpenCitations contributions via KOMET-developed software (GaziYucel account)
- [ ] Create statistics for potential impact of OJS citations
- [x] Store statistics in timestamped JSON file (komet_timeline.json)
- [ ] Add historical comparison visualizations

## Files

| File | Description |
|------|-------------|
| `komet_evaluation.ipynb` | Main analysis notebook |
| `komet_helpers.py` | Python helper functions for API queries |
| `komet_timeline.json` | Timestamped observations log (auto-updated, hierarchical format) |
| `komet_report_data.json` | Latest report snapshot |
| `docs/index.html` | HTML report for GitHub Pages (auto-generated) |
| `Makefile` | Build automation for local development and CI |
| `templates/collapsible/` | Custom nbconvert template for collapsible code cells |
| `CLAUDE.md` | Project context and AI assistant documentation |

## Related Repositories

- **OPTIMETA Citations Plugin**: https://github.com/TIBHannover/optimetaCitations
- **OPTIMETA Geo Plugin**: https://github.com/TIBHannover/optimetaGeo
- **OPTIMETA Plugin Shared**: https://github.com/TIBHannover/optimeta-plugin-shared
- **OPTIMAP**: https://optimap.science/
- **OpenCitations Crowdsourcing**: https://github.com/opencitations/crowdsourcing

## Usage

### Prerequisites

- Python 3.11+ (with `venv` module)
- Make

### Quick Start

```bash
# Create virtual environment and install dependencies
make install

# Run the evaluation notebook interactively
.venv/bin/jupyter notebook komet_evaluation.ipynb

# Or run helper module directly for quick test
.venv/bin/python komet_helpers.py
```

### Local Development

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

### Virtual Environment

The Makefile automatically creates and uses a `.venv` directory for Python dependencies. This ensures:

- Reproducible builds locally and in CI
- No interference with system Python packages
- Easy cleanup with `make clean-venv`

To start fresh with a clean environment:

```bash
make distclean   # Remove all generated files and venv
make update      # Recreate venv, install deps, run notebook, generate HTML
```

### Generating the Report Locally

To regenerate the HTML report for preview:

```bash
# Full update: execute notebook and generate HTML
make update

# Preview the generated HTML locally
make serve
# Then open http://localhost:8000 in your browser
```

The HTML report is generated with an informative title ("KOMET Project - Open Metadata Evaluation Report") and code cells are collapsed by default for cleaner output.

### PDF Generation

To generate a PDF report using typst:

```bash
make pdf    # Generates docs/komet_report.pdf
```

**Requirements for PDF generation:**
- [typst](https://typst.app/docs/guides/install/) CLI

The PDF is generated by converting the notebook to markdown via nbconvert, then compiling with typst using the cmarker package. Code cells are excluded; only narrative and visualizations are included.

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

### Annual Releases

A separate workflow (`.github/workflows/annual-release.yml`) creates a GitHub release at the end of each year:

- Runs automatically on December 31st at 23:00 UTC
- Generates fresh PDF report with year-end data
- Creates release `vYYYY` with:
  - `komet_report.pdf` - PDF report for offline reading
  - `komet_report_data.json` - Machine-readable metrics snapshot
  - `komet_timeline.json` - Historical time series data
- Includes key metrics in release notes

Can also be triggered manually to create releases for past years.

## Funding

This work is funded by the German Federal Ministry of Education and Research (BMBFTR) under grant number `16TOA039`.

![BMFTR Logo](https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/BMFTR_Logo.svg/320px-BMFTR_Logo.svg.png)

The KOMET project (Förderkennzeichen 16TOA039) is part of the funding initiative "Förderung von Projekten zur Etablierung einer gelebten Open-Access-Kultur in der deutschen Forschungs- und Wissenschaftspraxis."

## License

**Code**: CC-0 1.0

**Report outputs**: CC-BY 4.0

### External Data Sources

This project uses data from the following sources:

| Source | License | Link |
|--------|---------|------|
| Wikidata | CC0 1.0 | https://www.wikidata.org/wiki/Wikidata:Licensing |
| OpenCitations | CC0 1.0 | https://opencitations.net/about#licensing |
| GitHub API | GitHub Terms | https://docs.github.com/en/site-policy/github-terms |
