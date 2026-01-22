# KOMET Reports

Data reports on open metadata status by the KOMET project.

**Project Website**: https://projects.tib.eu/komet
**Predecessor**: OPTIMETA - https://projects.tib.eu/optimeta
**Funding**: BMBF (German Federal Ministry of Education and Research)

## About

This repository implements **AP 4.3: Evaluation** from the KOMET project proposal, tracking contributions to the open metadata commons from OJS-based Open Access journals.

**Primary target platform**: OpenCitations
**Secondary/monitoring**: Wikidata

## Methodology

### Goals

This evaluation tracks the contributions of the KOMET project (and its predecessor OPTIMETA) to the open metadata commons. The primary goal is to measure the impact of OJS plugins that enable journals to contribute citation and geospatial metadata to open knowledge bases.

**Key questions:**
- How many citation relationships have KOMET/OPTIMETA contributions added to OpenCitations?
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

**OpenCitations (Primary)**
- `opencitations_total_issues`: Total crowdsourcing issues in the repository
- `opencitations_komet_issues`: Issues created by KOMET team members
- `opencitations_komet_done`: Successfully processed KOMET contributions
- `opencitations_komet_pending`: KOMET contributions awaiting processing
- `opencitations_komet_invalid`: KOMET contributions marked as invalid

**Wikidata (Secondary/Monitoring)**
- `wikidata_p1343_scholarly_count`: Scholarly articles with "described by source" property (baseline reference)
- `wikidata_komet_provenance_count`: Items with KOMET/OPTIMETA provenance
- `wikidata_journal_{QID}_articles`: Article count per partner journal
- `wikidata_journal_{QID}_citations_p2860`: Outgoing citations per partner journal

### Partner Journals

The evaluation tracks 15 journals from 8 collaboration partners that have committed to testing OPTIMETA/KOMET plugins:

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

Statistics are stored in `komet_timeline.json` with the following approach:

1. **Timestamped observations**: Each metric value is recorded with ISO timestamps
2. **Change detection**: New entries are only added when values change; otherwise, only `last_seen` is updated
3. **Historical comparison**: Enables tracking trends over the project lifetime
4. **JSON format**: Human-readable and version-control friendly

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
- [x] Track OpenCitations contributions by KOMET team (GaziYucel)
- [ ] Create statistics for potential impact of OJS citations
- [x] Store statistics in timestamped JSON file (komet_timeline.json)
- [ ] Add historical comparison visualizations

### Automation & Infrastructure

- [x] Run Notebook once a week via CI (GitHub Actions)
- [x] Recalculate statistics weekly, only update timeline if values changed
- [ ] Add notification for significant changes

### Documentation & Branding

- [x] Add info/branding of KOMET to notebook
- [x] Add funder statement to README and notebook
- [x] Add extensive README with methodology description
- [ ] Create project logo/banner integration

## Files

| File | Description |
|------|-------------|
| `komet_evaluation.ipynb` | Main analysis notebook |
| `komet_helpers.py` | Python helper functions for API queries |
| `komet_timeline.json` | Timestamped observations log (auto-updated) |
| `komet_report_data.json` | Latest report snapshot |
| `docs/index.html` | HTML report for GitHub Pages (auto-generated) |
| `CLAUDE.md` | Project context and AI assistant documentation |

## Related Repositories

- **OPTIMETA Citations Plugin**: https://github.com/TIBHannover/optimetaCitations
- **OPTIMETA Geo Plugin**: https://github.com/TIBHannover/optimetaGeo
- **OPTIMETA Plugin Shared**: https://github.com/TIBHannover/optimeta-plugin-shared
- **OPTIMAP**: https://optimap.science/
- **OpenCitations Crowdsourcing**: https://github.com/opencitations/crowdsourcing

## Usage

```bash
# Install dependencies
pip install requests jupyter

# Run the evaluation notebook
jupyter notebook komet_evaluation.ipynb

# Or run helper module directly for quick test
python komet_helpers.py
```

## Funding

This work is funded by the German Federal Ministry of Education and Research (BMBF) under grant number 16TOA039.

![BMBF Logo](https://www.bmbf.de/SiteGlobals/Frontend/Images/icons/logo.svg?__blob=normal)

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
