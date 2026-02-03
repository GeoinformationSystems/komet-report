"""
KOMET Report Helper Functions

Helper module for querying Wikidata SPARQL and OpenCitations/GitHub APIs
to evaluate KOMET project contributions to the metadata commons.
"""

import requests
import json
import time
from typing import Optional, Dict, List, Any
from datetime import datetime


# =============================================================================
# Configuration
# =============================================================================

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
WIKIDATA_SCHOLARLY_ENDPOINT = "https://query-scholarly.wikidata.org/sparql"
GITHUB_API_BASE = "https://api.github.com"
OPENCITATIONS_REPO = "opencitations/crowdsourcing"

# GitHub handles associated with KOMET-developed software deposits
# The KOMET Citations Plugin automatically creates issues using these accounts
KOMET_CONTRIBUTORS = [
    "GaziYucel",  # Gazi Yuecel, TIB - KOMET plugin developer
    # Add more GitHub handles associated with KOMET software here
]

# User-Agent for API requests (required by Wikidata)
HEADERS = {
    "User-Agent": "KOMET-Report/1.0 (https://projects.tib.eu/komet; mailto:daniel.nuest@tu-dresden.de)",
    "Accept": "application/sparql-results+json"
}

# Timeline log file for tracking statistics over time
TIMELINE_LOG_FILE = "komet_timeline.json"

# =============================================================================
# KOMET Collaboration Partners
# Source: https://projects.tib.eu/optimeta/en/ (from related OPTIMETA project)
# Data from: "Journals der Partner" document (2022-01-26)
# =============================================================================

COLLABORATION_PARTNERS = {
    "journals": [
        # --- KIM Universität Konstanz ---
        {
            "name": "Journal of South Asian Linguistics",
            "partner": "KIM Universität Konstanz",
            "url": "https://ojs.ub.uni-konstanz.de/jsal/",
            "wikidata_qid": "Q122948152",
            "ojs_version": "3.3.0.14",
            "baseline_2022": {"wikidata_articles": 0, "wikidata_with_citations": 0, "openalex": 0}
        },
        # --- WWU E-Journals Münster ---
        {
            "name": "Free Neuropathology",
            "partner": "WWU Münster",
            "url": "https://www.uni-muenster.de/Ejournals/index.php/fnp",
            "wikidata_qid": "Q108455809",
            "ojs_version": "3.3.0.13",
            "baseline_2022": {"wikidata_articles": 0, "wikidata_with_citations": 0, "openalex": 0}
        },
        {
            "name": "Jahrbuch für Christliche Sozialwissenschaften",
            "partner": "WWU Münster",
            "url": "https://www.uni-muenster.de/Ejournals/index.php/jcsw",
            "wikidata_qid": "Q1678617",
            "ojs_version": "3.3.0.13",
            "baseline_2022": {"wikidata_articles": 0, "wikidata_with_citations": 0, "openalex": 850}
        },
        # --- e-journals Julius Kühn-Institut ---
        {
            "name": "Journal für Kulturpflanzen",
            "partner": "Julius Kühn-Institut",
            "url": "https://ojs.openagrar.de/index.php/Kulturpflanzenjournal",
            "wikidata_qid": "Q1455822",
            "ojs_version": "3.3.0.8",
            "baseline_2022": {"wikidata_articles": 0, "wikidata_with_citations": 0, "openalex": 558}
        },
        {
            "name": "VITIS - Journal of Grapevine Research",
            "partner": "Julius Kühn-Institut",
            "url": "https://ojs.openagrar.de/index.php/VITIS",
            "wikidata_qid": "Q15756080",
            "ojs_version": "3.3.0.8",
            "baseline_2022": {"wikidata_articles": 0, "wikidata_with_citations": 0, "openalex": 1762}
        },
        {
            "name": "Journal of Applied Botany and Food Quality",
            "partner": "Julius Kühn-Institut",
            "url": "https://ojs.openagrar.de/index.php/JABFQ",
            "wikidata_qid": "Q15764825",
            "ojs_version": "3.3.0.8",
            "baseline_2022": {"wikidata_articles": 3, "wikidata_with_citations": 0, "openalex": 419}
        },
        # --- heiJOURNALS Heidelberg ---
        {
            "name": "Francia-Recensio",
            "partner": "heiJOURNALS Heidelberg",
            "url": "https://journals.ub.uni-heidelberg.de/index.php/frrec",
            "wikidata_qid": "Q101247086",
            "ojs_version": "3.2.1.4",
            "baseline_2022": {"wikidata_articles": 1, "wikidata_with_citations": 0, "openalex": 1096}
        },
        {
            "name": "Heidelberger Beiträge zum Finanz- und Steuerrecht",
            "partner": "heiJOURNALS Heidelberg",
            "url": "https://journals.ub.uni-heidelberg.de/index.php/hbfsr",
            "wikidata_qid": "Q105103105",
            "ojs_version": "3.2.1.4",
            "baseline_2022": {"wikidata_articles": 0, "wikidata_with_citations": 0, "openalex": 0}
        },
        {
            "name": "Informationspraxis",
            "partner": "heiJOURNALS Heidelberg",
            "url": "https://journals.ub.uni-heidelberg.de/index.php/ip",
            "wikidata_qid": "Q46478422",
            "ojs_version": "3.2.1.4",
            "baseline_2022": {"wikidata_articles": 55, "wikidata_with_citations": 3, "openalex": 43},
            "notes": "Journal discontinued"
        },
        {
            "name": "International Journal of Dream Research",
            "partner": "heiJOURNALS Heidelberg",
            "url": "https://journals.ub.uni-heidelberg.de/index.php/IJoDR",
            "wikidata_qid": "Q96332444",
            "ojs_version": "3.2.1.4",
            "baseline_2022": {"wikidata_articles": 0, "wikidata_with_citations": 0, "openalex": 352}
        },
        {
            "name": "Journal of Dynamic Decision Making",
            "partner": "heiJOURNALS Heidelberg",
            "url": "https://journals.ub.uni-heidelberg.de/index.php/jddm",
            "wikidata_qid": "Q50817185",
            "ojs_version": "3.2.1.4",
            "baseline_2022": {"wikidata_articles": 0, "wikidata_with_citations": 0, "openalex": 18}
        },
        # --- DAI ---
        {
            "name": "Archäologischer Anzeiger",
            "partner": "Deutsches Archäologisches Institut",
            "url": "https://publications.dainst.org/journals/index.php/aa",
            "wikidata_qid": "Q636752",
            "ojs_version": "3.4.0.6",
            "baseline_2022": {"wikidata_articles": 0, "wikidata_with_citations": 0, "openalex": 224}
        },
        # --- JOSIS ---
        {
            "name": "Journal of Spatial Information Science",
            "partner": "JOSIS / TU Dresden",
            "url": "https://josis.org",
            "wikidata_qid": "Q50814880",
            "ojs_version": "3.3.0.6",
            "baseline_2022": {"wikidata_articles": 25, "wikidata_with_citations": 0, "openalex": 201}
        },
        # --- ZHB Luzern ---
        {
            "name": "Cognitio",
            "partner": "ZHB Luzern",
            "url": "https://cognitio-zeitschrift.ch",
            "wikidata_qid": "Q111049844",
            "ojs_version": "3.3.0.12",
            "baseline_2022": {"wikidata_articles": 31, "wikidata_with_citations": 0, "openalex": 0}
        },
        {
            "name": "itdb - inter- und transdisziplinäre Bildung",
            "partner": "ZHB Luzern",
            "url": "https://www.itdb.ch",
            "wikidata_qid": "Q107074231",
            "ojs_version": "3.3.0.12",
            "baseline_2022": {"wikidata_articles": 13, "wikidata_with_citations": 0, "openalex": 0}
        },
    ],
    "journals_without_wikidata": [
        # Journals from partners that don't have Wikidata entries yet
        {"name": "Formal Approaches to South Asian Languages", "partner": "KIM Konstanz"},
        {"name": "Journal of Historical Syntax", "partner": "KIM Konstanz"},
        {"name": "KIM Kompakt", "partner": "KIM Konstanz"},
        {"name": "The Byzantine Review", "partner": "WWU Münster"},
        {"name": "Mittelalter Digital", "partner": "WWU Münster"},
        {"name": "Volcanica", "partner": "Independent", "url": "https://www.jvolcanica.org/"},
        {"name": "GEUS Bulletin", "partner": "Independent", "url": "https://geusbulletin.org"},
    ],
    "platforms": [
        {"name": "KIM - Universität Konstanz", "url": "https://www.kim.uni-konstanz.de/"},
        {"name": "WWU E-Journals Münster", "url": "https://www.uni-muenster.de/Ejournals/"},
        {"name": "e-journals Julius Kühn-Institut", "url": "https://ojs.openagrar.de"},
        {"name": "heiJOURNALS Heidelberg", "url": "https://journals.ub.uni-heidelberg.de"},
        {"name": "TIB Open Publishing", "url": "https://www.tib-op.org/"},
        {"name": "ZHB Luzern", "url": "https://www.zhbluzern.ch/"},
    ],
    "infrastructure": [
        {"name": "Public Knowledge Project (PKP)", "url": "https://pkp.sfu.ca/"},
        {"name": "OpenCitations", "url": "https://opencitations.net/", "notes": "Primary target platform"},
    ]
}


def get_journals_with_wikidata() -> List[Dict]:
    """Return only journals that have a Wikidata QID."""
    return [j for j in COLLABORATION_PARTNERS["journals"] if j.get("wikidata_qid")]


def get_all_journal_qids() -> List[str]:
    """Return list of all Wikidata QIDs for partner journals."""
    return [j["wikidata_qid"] for j in COLLABORATION_PARTNERS["journals"] if j.get("wikidata_qid")]


# =============================================================================
# Wikidata SPARQL Queries
# =============================================================================

def query_wikidata(sparql_query: str, timeout: int = 60, use_scholarly_endpoint: bool = False) -> Optional[Dict]:
    """
    Execute a SPARQL query against the Wikidata Query Service.

    Args:
        sparql_query: The SPARQL query string
        timeout: Request timeout in seconds
        use_scholarly_endpoint: If True, use the scholarly-specific endpoint
                                (better for queries focused on Q13442814 scholarly articles)

    Returns:
        JSON response as dict, or None if query fails
    """
    endpoint = WIKIDATA_SCHOLARLY_ENDPOINT if use_scholarly_endpoint else WIKIDATA_SPARQL_ENDPOINT
    try:
        response = requests.get(
            endpoint,
            params={"query": sparql_query, "format": "json"},
            headers=HEADERS,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print(f"Query timed out after {timeout}s")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Query failed: {e}")
        return None


def count_scholarly_articles() -> Optional[int]:
    """
    Count total scholarly articles (Q13442814) in Wikidata.
    Note: This query may timeout due to the large dataset (~37M items).
    """
    query = """
    SELECT (COUNT(?item) AS ?count) WHERE {
      ?item wdt:P31 wd:Q13442814 .
    }
    """
    result = query_wikidata(query, timeout=120)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def count_p1343_scholarly_articles() -> Optional[int]:
    """
    Count scholarly articles that have P1343 (described by source).
    Expected to be very low (~14 items based on analysis).
    """
    query = """
    SELECT (COUNT(?item) AS ?count) WHERE {
      ?item wdt:P31/wdt:P279* wd:Q13442814 .
      ?item wdt:P1343 ?source .
    }
    """
    result = query_wikidata(query, timeout=60)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def get_p1343_scholarly_examples(limit: int = 50) -> List[Dict]:
    """
    Get examples of scholarly articles with P1343 (described by source).
    """
    query = f"""
    SELECT ?item ?itemLabel ?source ?sourceLabel WHERE {{
      ?item wdt:P31/wdt:P279* wd:Q13442814 .
      ?item wdt:P1343 ?source .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
    }}
    LIMIT {limit}
    """
    result = query_wikidata(query, timeout=60)
    if result and result.get("results", {}).get("bindings"):
        return result["results"]["bindings"]
    return []


def count_citations_p2860() -> Optional[int]:
    """
    Count total P2860 (cites work) relationships.
    Note: May timeout - Wikidata has ~3.4M citation relationships.
    """
    query = """
    SELECT (COUNT(?citation) AS ?count) WHERE {
      ?item wdt:P2860 ?citation .
    }
    """
    result = query_wikidata(query, timeout=120)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def get_scholarly_work_types(limit: int = 30) -> List[Dict]:
    """
    Get breakdown of publication/scholarly work types in Wikidata.
    """
    query = f"""
    SELECT ?type ?typeLabel (COUNT(?item) AS ?count) WHERE {{
      ?item wdt:P31 ?type .
      ?type wdt:P279* wd:Q732577 .  # subclass of publication
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
    }}
    GROUP BY ?type ?typeLabel
    ORDER BY DESC(?count)
    LIMIT {limit}
    """
    result = query_wikidata(query, timeout=120)
    if result and result.get("results", {}).get("bindings"):
        return result["results"]["bindings"]
    return []


def search_komet_provenance_wikidata() -> List[Dict]:
    """
    Search for Wikidata items that reference KOMET as source.
    Checks P1343 values for mentions of the project.
    """
    query = """
    SELECT ?item ?itemLabel ?source ?sourceLabel WHERE {
      ?item wdt:P1343 ?source .
      ?source rdfs:label ?sourceLabel .
      FILTER(CONTAINS(LCASE(?sourceLabel), "komet"))
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
    }
    LIMIT 100
    """
    result = query_wikidata(query, timeout=60)
    if result and result.get("results", {}).get("bindings"):
        return result["results"]["bindings"]
    return []


# =============================================================================
# OpenCitations Index API Functions
# =============================================================================

OPENCITATIONS_API_BASE = "https://api.opencitations.net/index/v2"


def get_journal_citation_count_opencitations(issn: str) -> Optional[int]:
    """
    Get total incoming citations for all articles in a journal from OpenCitations.

    Uses the venue-citation-count endpoint which returns the number of
    citations to all articles published in the journal identified by ISSN.

    Args:
        issn: Journal ISSN (e.g., "0138-9130")

    Returns:
        Total citation count or None if query failed
    """
    if not issn:
        return None

    # Clean ISSN (remove any prefix)
    issn = issn.replace("issn:", "").strip()

    url = f"{OPENCITATIONS_API_BASE}/venue-citation-count/issn:{issn}"
    headers = {
        "Accept": "application/json",
        "User-Agent": HEADERS["User-Agent"]
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        if data and len(data) > 0 and "count" in data[0]:
            return int(data[0]["count"])
    except requests.exceptions.RequestException as e:
        print(f"OpenCitations API error for ISSN {issn}: {e}")
    except (ValueError, KeyError, IndexError):
        pass

    return None


def get_article_citation_count_opencitations(doi: str) -> Optional[int]:
    """
    Get incoming citation count for a specific article from OpenCitations.

    Args:
        doi: Article DOI (e.g., "10.1186/1756-8722-6-59")

    Returns:
        Citation count or None if query failed
    """
    if not doi:
        return None

    # Clean DOI
    doi = doi.replace("doi:", "").replace("https://doi.org/", "").strip()

    url = f"{OPENCITATIONS_API_BASE}/citation-count/doi:{doi}"
    headers = {
        "Accept": "application/json",
        "User-Agent": HEADERS["User-Agent"]
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        if data and len(data) > 0 and "count" in data[0]:
            return int(data[0]["count"])
    except requests.exceptions.RequestException as e:
        print(f"OpenCitations API error for DOI {doi}: {e}")
    except (ValueError, KeyError, IndexError):
        pass

    return None


def get_journal_opencitations_stats(issn: str) -> Dict[str, Any]:
    """
    Get OpenCitations statistics for a journal.

    Returns:
        Dict with citation_count and query_timestamp
    """
    return {
        "issn": issn,
        "citation_count": get_journal_citation_count_opencitations(issn),
        "query_timestamp": format_timestamp()
    }


# =============================================================================
# GitHub API Functions (OpenCitations Crowdsourcing)
# =============================================================================

def get_github_issues(
    repo: str = OPENCITATIONS_REPO,
    state: str = "all",
    per_page: int = 100,
    page: int = 1,
    token: Optional[str] = None
) -> List[Dict]:
    """
    Fetch issues from a GitHub repository.

    Args:
        repo: Repository in format "owner/repo"
        state: "open", "closed", or "all"
        per_page: Number of issues per page (max 100)
        page: Page number for pagination
        token: Optional GitHub personal access token for higher rate limits

    Returns:
        List of issue dictionaries
    """
    url = f"{GITHUB_API_BASE}/repos/{repo}/issues"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    params = {
        "state": state,
        "per_page": per_page,
        "page": page
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"GitHub API request failed: {e}")
        return []


def get_all_opencitations_issues(token: Optional[str] = None) -> List[Dict]:
    """
    Fetch all issues from the OpenCitations crowdsourcing repository.
    Handles pagination automatically.
    """
    all_issues = []
    page = 1

    while True:
        issues = get_github_issues(
            repo=OPENCITATIONS_REPO,
            state="all",
            per_page=100,
            page=page,
            token=token
        )
        if not issues:
            break
        all_issues.extend(issues)
        if len(issues) < 100:
            break
        page += 1
        time.sleep(0.5)  # Rate limiting

    return all_issues


def filter_komet_contributions(
    issues: List[Dict],
    contributors: List[str] = KOMET_CONTRIBUTORS
) -> List[Dict]:
    """
    Filter issues to only those created by KOMET contributors.

    Args:
        issues: List of GitHub issue dictionaries
        contributors: List of GitHub usernames to filter by

    Returns:
        Filtered list of issues from KOMET contributors
    """
    return [
        issue for issue in issues
        if issue.get("user", {}).get("login") in contributors
    ]


def parse_opencitations_issue(issue: Dict) -> Dict[str, Any]:
    """
    Parse an OpenCitations crowdsourcing issue to extract key metadata.

    Expected title format: "deposit {domain} {identifier}"

    Returns dict with:
        - issue_number
        - title
        - state (open/closed)
        - labels
        - creator
        - created_at
        - domain (extracted from title)
        - identifier (extracted from title)
        - status (derived from labels: to_be_processed, done, invalid, rejected)
    """
    title = issue.get("title", "")
    labels = [label.get("name", "") for label in issue.get("labels", [])]

    # Parse title format: "deposit {domain} {identifier}"
    parts = title.split(" ", 2)
    domain = parts[1] if len(parts) > 1 else None
    identifier = parts[2] if len(parts) > 2 else None

    # Determine status from labels
    status = "unknown"
    if "done" in labels:
        status = "done"
    elif "to be processed" in labels:
        status = "to_be_processed"
    elif "invalid" in labels:
        status = "invalid"
    elif "rejected" in labels:
        status = "rejected"

    return {
        "issue_number": issue.get("number"),
        "title": title,
        "state": issue.get("state"),
        "labels": labels,
        "creator": issue.get("user", {}).get("login"),
        "created_at": issue.get("created_at"),
        "closed_at": issue.get("closed_at"),
        "domain": domain,
        "identifier": identifier,
        "status": status,
        "url": issue.get("html_url")
    }


def summarize_opencitations_contributions(issues: List[Dict]) -> Dict[str, Any]:
    """
    Generate summary statistics for OpenCitations contributions.
    """
    parsed = [parse_opencitations_issue(issue) for issue in issues]

    # Filter out pull requests (they also appear in issues endpoint)
    parsed = [p for p in parsed if "pull_request" not in issues[parsed.index(p)]]

    status_counts = {}
    creator_counts = {}
    domain_counts = {}

    for p in parsed:
        status = p["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

        creator = p["creator"]
        creator_counts[creator] = creator_counts.get(creator, 0) + 1

        domain = p["domain"]
        if domain:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

    return {
        "total_issues": len(parsed),
        "status_breakdown": status_counts,
        "by_creator": creator_counts,
        "by_domain": domain_counts,
        "parsed_issues": parsed
    }


# =============================================================================
# Journal Lookup Functions (Wikidata)
# =============================================================================

def search_journal_wikidata(journal_name: str) -> List[Dict]:
    """
    Search for a journal in Wikidata by name.
    Returns matching items that are instances of academic journal (Q737498).
    """
    # Escape quotes in journal name
    escaped_name = journal_name.replace('"', '\\"')
    query = f"""
    SELECT ?item ?itemLabel ?issn WHERE {{
      ?item wdt:P31/wdt:P279* wd:Q737498 .  # academic journal or subclass
      ?item rdfs:label ?label .
      FILTER(CONTAINS(LCASE(?label), LCASE("{escaped_name}")))
      OPTIONAL {{ ?item wdt:P236 ?issn . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
    }}
    LIMIT 10
    """
    result = query_wikidata(query, timeout=30)
    if result and result.get("results", {}).get("bindings"):
        return result["results"]["bindings"]
    return []


def get_journal_by_issn(issn: str) -> Optional[Dict]:
    """
    Look up a journal in Wikidata by ISSN.
    """
    query = f"""
    SELECT ?item ?itemLabel ?title WHERE {{
      ?item wdt:P236 "{issn}" .
      OPTIONAL {{ ?item wdt:P1476 ?title . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
    }}
    LIMIT 1
    """
    result = query_wikidata(query, timeout=30)
    if result and result.get("results", {}).get("bindings"):
        return result["results"]["bindings"][0]
    return None


def count_journal_articles_wikidata(journal_qid: str) -> Optional[int]:
    """
    Count articles published in a specific journal (by Wikidata QID).
    Uses P1433 (published in) property.
    """
    query = f"""
    SELECT (COUNT(?article) AS ?count) WHERE {{
      ?article wdt:P1433 wd:{journal_qid} .
    }}
    """
    result = query_wikidata(query, timeout=60)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def count_journal_citations_p2860(journal_qid: str) -> Optional[int]:
    """
    Count P2860 (cites work) relationships where the citing work
    is published in a specific journal.
    """
    query = f"""
    SELECT (COUNT(?citation) AS ?count) WHERE {{
      ?article wdt:P1433 wd:{journal_qid} .
      ?article wdt:P2860 ?citation .
    }}
    """
    result = query_wikidata(query, timeout=60)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def get_journal_stats_wikidata(journal_qid: str) -> Dict[str, Any]:
    """
    Get comprehensive statistics for a journal from Wikidata.
    """
    article_count = count_journal_articles_wikidata(journal_qid)
    citation_count = count_journal_citations_p2860(journal_qid)

    return {
        "qid": journal_qid,
        "articles_in_wikidata": article_count,
        "outgoing_citations_p2860": citation_count,
        "query_timestamp": format_timestamp()
    }


def get_journal_metadata_wikidata(journal_qid: str) -> Dict[str, Any]:
    """
    Get journal metadata from Wikidata including ISSN and publisher.

    Properties queried:
    - P236: ISSN
    - P123: publisher
    - P1476: title
    """
    query = f"""
    SELECT ?journal ?journalLabel ?issn ?publisher ?publisherLabel ?title WHERE {{
      BIND(wd:{journal_qid} AS ?journal)
      OPTIONAL {{ ?journal wdt:P236 ?issn . }}
      OPTIONAL {{ ?journal wdt:P123 ?publisher . }}
      OPTIONAL {{ ?journal wdt:P1476 ?title . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,de" . }}
    }}
    LIMIT 1
    """
    result = query_wikidata(query, timeout=30)

    metadata = {
        "qid": journal_qid,
        "name": None,
        "issn": None,
        "publisher": None,
        "publisher_qid": None
    }

    if result and result.get("results", {}).get("bindings"):
        binding = result["results"]["bindings"][0]
        metadata["name"] = binding.get("journalLabel", {}).get("value")
        metadata["issn"] = binding.get("issn", {}).get("value")
        metadata["publisher"] = binding.get("publisherLabel", {}).get("value")
        if binding.get("publisher"):
            metadata["publisher_qid"] = binding["publisher"]["value"].split("/")[-1]

    return metadata


def get_journal_metadata_crossref(issn: str) -> Optional[Dict[str, Any]]:
    """
    Get journal metadata from Crossref API using ISSN.

    Returns publisher name and other metadata not available in Wikidata.
    """
    if not issn:
        return None

    url = f"https://api.crossref.org/journals/{issn}"
    headers = {
        "User-Agent": "KOMET-Report/1.0 (https://projects.tib.eu/komet; mailto:daniel.nuest@tu-dresden.de)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            message = data.get("message", {})
            return {
                "title": message.get("title"),
                "publisher": message.get("publisher"),
                "issn": message.get("ISSN", []),
                "subjects": message.get("subjects", []),
                "counts": message.get("counts", {})
            }
    except requests.exceptions.RequestException:
        pass

    return None


def count_journal_articles_with_coordinates(journal_qid: str) -> Optional[int]:
    """
    Count articles from a journal that have coordinate location (P625).
    Uses scholarly endpoint for better performance.
    """
    query = f"""
    SELECT (COUNT(?article) AS ?count) WHERE {{
      ?article wdt:P1433 wd:{journal_qid} .
      ?article wdt:P625 ?coord .
    }}
    """
    result = query_wikidata(query, timeout=60, use_scholarly_endpoint=True)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def count_journal_articles_with_bounding_box(journal_qid: str) -> Optional[int]:
    """
    Count articles from a journal that have any bounding box property (P1332-P1335).
    """
    query = f"""
    SELECT (COUNT(DISTINCT ?article) AS ?count) WHERE {{
      ?article wdt:P1433 wd:{journal_qid} .
      {{ ?article wdt:P1332 ?n . }}
      UNION {{ ?article wdt:P1333 ?s . }}
      UNION {{ ?article wdt:P1334 ?e . }}
      UNION {{ ?article wdt:P1335 ?w . }}
    }}
    """
    result = query_wikidata(query, timeout=60, use_scholarly_endpoint=True)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def count_journal_articles_with_temporal_scope(journal_qid: str) -> Optional[int]:
    """
    Count articles from a journal that have temporal scope (P580 or P582).
    """
    query = f"""
    SELECT (COUNT(DISTINCT ?article) AS ?count) WHERE {{
      ?article wdt:P1433 wd:{journal_qid} .
      {{ ?article wdt:P580 ?start . }}
      UNION {{ ?article wdt:P582 ?end . }}
    }}
    """
    result = query_wikidata(query, timeout=60, use_scholarly_endpoint=True)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def count_journal_articles_with_geographic_subject(journal_qid: str) -> Optional[int]:
    """
    Count articles from a journal where main subject (P921) links to
    an item with coordinates.
    """
    query = f"""
    SELECT (COUNT(DISTINCT ?article) AS ?count) WHERE {{
      ?article wdt:P1433 wd:{journal_qid} .
      ?article wdt:P921 ?subject .
      ?subject wdt:P625 ?coord .
    }}
    """
    result = query_wikidata(query, timeout=90, use_scholarly_endpoint=True)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def get_journal_geospatial_stats(journal_qid: str) -> Dict[str, Any]:
    """
    Get comprehensive geospatial/temporal statistics for a journal.

    Returns counts for:
    - Articles with direct coordinates (P625)
    - Articles with bounding box (P1332-P1335)
    - Articles with temporal scope (P580/P582)
    - Articles with geographic main subject (P921 → geo item)
    """
    return {
        "qid": journal_qid,
        "articles_with_coordinates": count_journal_articles_with_coordinates(journal_qid),
        "articles_with_bounding_box": count_journal_articles_with_bounding_box(journal_qid),
        "articles_with_temporal_scope": count_journal_articles_with_temporal_scope(journal_qid),
        "articles_with_geo_subject": count_journal_articles_with_geographic_subject(journal_qid),
        "query_timestamp": format_timestamp()
    }


def get_journal_full_metadata(journal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get full metadata for a journal combining local config, Wikidata, and Crossref.

    Args:
        journal: Journal dict from COLLABORATION_PARTNERS with at least 'wikidata_qid'

    Returns:
        Enhanced journal metadata with ISSN and publisher from multiple sources
    """
    qid = journal.get("wikidata_qid")

    # Start with local config data
    result = {
        "name": journal.get("name"),
        "qid": qid,
        "partner": journal.get("partner"),
        "url": journal.get("url"),
        "issn": None,
        "publisher": None,
        "publisher_source": None
    }

    # Enhance from Wikidata
    if qid:
        wd_meta = get_journal_metadata_wikidata(qid)
        if wd_meta.get("issn"):
            result["issn"] = wd_meta["issn"]
        if wd_meta.get("publisher"):
            result["publisher"] = wd_meta["publisher"]
            result["publisher_source"] = "wikidata"
        if not result["name"] and wd_meta.get("name"):
            result["name"] = wd_meta["name"]

    # Enhance from Crossref if we have ISSN but no publisher
    if result["issn"] and not result["publisher"]:
        cr_meta = get_journal_metadata_crossref(result["issn"])
        if cr_meta and cr_meta.get("publisher"):
            result["publisher"] = cr_meta["publisher"]
            result["publisher_source"] = "crossref"

    return result


# =============================================================================
# Timeline Logging Functions (v2.0 - Hierarchical Format)
# =============================================================================

def load_timeline(filepath: str = TIMELINE_LOG_FILE) -> Dict[str, Any]:
    """
    Load the timeline log file. Creates empty structure if not exists.
    Uses v2.0 hierarchical format with grouped metrics and time series.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Check for v2.0 format
            if "metadata" in data and "metrics" in data:
                return data
            # Migrate v1.0 format (not implemented - start fresh)
            return _create_empty_timeline()
    except FileNotFoundError:
        return _create_empty_timeline()


def _create_empty_timeline() -> Dict[str, Any]:
    """Create empty v2.0 timeline structure."""
    return {
        "metadata": {
            "created": format_timestamp(),
            "last_updated": None,
            "version": "2.0",
            "description": "KOMET project evaluation metrics timeline"
        },
        "metrics": {
            "wikidata": {
                "description": "Wikidata scholarly graph metrics",
                "journals": {
                    "description": "Partner journal statistics from Wikidata"
                }
            },
            "opencitations": {
                "description": "OpenCitations crowdsourcing metrics"
            }
        }
    }


def save_timeline(timeline: Dict[str, Any], filepath: str = TIMELINE_LOG_FILE) -> None:
    """Save the timeline log file."""
    timeline["metadata"]["last_updated"] = format_timestamp()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False, default=str)


def add_observation(
    timeline: Dict[str, Any],
    metric_path: str,
    value: Any,
    source: str,
    notes: Optional[str] = None,
    metric_name: Optional[str] = None,
    metric_description: Optional[str] = None
) -> bool:
    """
    Add an observation to the timeline using hierarchical path.

    Only adds a new entry if the value has changed from the last observation.

    Args:
        timeline: The timeline dict to update
        metric_path: Dot-separated path (e.g., "wikidata.p1343_scholarly_count"
                     or "wikidata.journals.Q123456.articles")
        value: The observed value
        source: Data source (e.g., "wikidata", "opencitations")
        notes: Optional notes (stored at metric level, not per observation)
        metric_name: Human-readable metric name (for new metrics)
        metric_description: Description (for new metrics)

    Returns:
        True if a new entry was added, False if value unchanged
    """
    timestamp = format_timestamp()
    parts = metric_path.split(".")

    # Navigate/create path to metric
    current = timeline["metrics"]
    for i, part in enumerate(parts[:-1]):
        if part not in current:
            current[part] = {}
        current = current[part]

    metric_key = parts[-1]

    # Create metric if it doesn't exist
    if metric_key not in current:
        current[metric_key] = {
            "series": []
        }
        if metric_name:
            current[metric_key]["name"] = metric_name
        if metric_description:
            current[metric_key]["description"] = metric_description
        if notes:
            current[metric_key]["notes"] = notes
        current[metric_key]["unit"] = "count"

    metric = current[metric_key]
    series = metric.get("series", [])

    # Check if value changed
    if series and series[-1]["v"] == value:
        return False

    # Add new observation
    series.append({"t": timestamp, "v": value})
    metric["series"] = series
    return True


def add_journal_observation(
    timeline: Dict[str, Any],
    qid: str,
    metric_type: str,
    value: Any,
    journal_name: Optional[str] = None,
    partner: Optional[str] = None
) -> bool:
    """
    Add an observation for a partner journal.

    Args:
        timeline: The timeline dict
        qid: Wikidata QID (e.g., "Q123456")
        metric_type: "articles" or "citations_p2860"
        value: The observed value
        journal_name: Journal name (for new entries)
        partner: Partner organization name (for new entries)

    Returns:
        True if new entry added, False if unchanged
    """
    journals = timeline["metrics"]["wikidata"].setdefault("journals", {
        "description": "Partner journal statistics from Wikidata"
    })

    # Create journal entry if needed
    if qid not in journals or not isinstance(journals[qid], dict):
        journals[qid] = {}

    journal = journals[qid]
    if journal_name and "name" not in journal:
        journal["name"] = journal_name
    if partner and "partner" not in journal:
        journal["partner"] = partner

    # Create metric type if needed
    if metric_type not in journal:
        journal[metric_type] = {"series": []}

    series = journal[metric_type].get("series", [])

    # Check if value changed
    if series and series[-1]["v"] == value:
        return False

    timestamp = format_timestamp()
    series.append({"t": timestamp, "v": value})
    journal[metric_type]["series"] = series
    return True


def get_metric_series(timeline: Dict[str, Any], metric_path: str) -> List[Dict]:
    """
    Get time series for a specific metric.

    Args:
        metric_path: Dot-separated path (e.g., "wikidata.p1343_scholarly_count")

    Returns:
        List of {t, v} observations
    """
    parts = metric_path.split(".")
    current = timeline["metrics"]

    for part in parts:
        if part not in current:
            return []
        current = current[part]

    return current.get("series", [])


def get_latest_value(timeline: Dict[str, Any], metric_path: str) -> Optional[Any]:
    """Get the most recent value for a metric."""
    series = get_metric_series(timeline, metric_path)
    return series[-1]["v"] if series else None


def get_all_latest_metrics(timeline: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get the most recent value for all metrics (flattened view).
    """
    latest = {}

    def collect_metrics(obj: Dict, path: str = ""):
        for key, value in obj.items():
            if key in ("description", "name", "notes", "unit", "partner"):
                continue
            current_path = f"{path}.{key}" if path else key
            if isinstance(value, dict):
                if "series" in value and value["series"]:
                    latest[current_path] = {
                        "value": value["series"][-1]["v"],
                        "timestamp": value["series"][-1]["t"],
                        "name": value.get("name", key)
                    }
                else:
                    collect_metrics(value, current_path)

    collect_metrics(timeline["metrics"])
    return latest


# =============================================================================
# Utility Functions
# =============================================================================

def save_json(data: Any, filepath: str) -> None:
    """Save data to JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def load_json(filepath: str) -> Any:
    """Load data from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def format_timestamp() -> str:
    """Return current timestamp in ISO format."""
    return datetime.utcnow().isoformat() + "Z"


# =============================================================================
# Geospatial & Temporal Metadata Queries for Scholarly Works
# Based on OPTIMAP export model and Wikidata conventions
# =============================================================================

# Properties used for geospatial/temporal metadata (from OPTIMAP analysis)
GEOSPATIAL_PROPERTIES = {
    "P625": "coordinate location",          # Center point
    "P1332": "northernmost point",          # Bounding box north
    "P1333": "southernmost point",          # Bounding box south
    "P1334": "easternmost point",           # Bounding box east
    "P1335": "westernmost point",           # Bounding box west
    "P921": "main subject",                 # Link to geographic items
    "P3896": "geoshape",                    # GeoJSON shape (polygon/line) on Commons
}

TEMPORAL_PROPERTIES = {
    "P577": "publication date",             # Standard for articles
    "P580": "start time",                   # Research period start
    "P582": "end time",                     # Research period end
    "P585": "point in time",                # Specific time reference
}


def count_scholarly_articles_with_coordinates() -> Optional[int]:
    """
    Count scholarly articles that have direct coordinate location (P625).
    This is rare - OPTIMAP exports use this approach.
    Uses the scholarly-specific Wikidata endpoint for better performance.
    """
    query = """
    SELECT (COUNT(DISTINCT ?article) AS ?count) WHERE {
      ?article wdt:P31 wd:Q13442814 .
      ?article wdt:P625 ?coord .
    }
    """
    result = query_wikidata(query, timeout=120, use_scholarly_endpoint=True)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def count_scholarly_articles_with_bounding_box() -> Optional[int]:
    """
    Count scholarly articles with bounding box properties (P1332-P1335).
    OPTIMAP exports geographic extent using these properties.
    Uses the scholarly-specific Wikidata endpoint for better performance.
    """
    query = """
    SELECT (COUNT(DISTINCT ?article) AS ?count) WHERE {
      ?article wdt:P31 wd:Q13442814 .
      { ?article wdt:P1332 ?north . }
      UNION { ?article wdt:P1333 ?south . }
      UNION { ?article wdt:P1334 ?east . }
      UNION { ?article wdt:P1335 ?west . }
    }
    """
    result = query_wikidata(query, timeout=120, use_scholarly_endpoint=True)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def count_scholarly_articles_with_geographic_subject() -> Optional[int]:
    """
    Count scholarly articles where main subject (P921) links to an item
    with coordinates. This is the recommended Wikidata approach for
    indicating geographic relevance.
    Uses the scholarly-specific Wikidata endpoint for better performance.
    """
    query = """
    SELECT (COUNT(DISTINCT ?article) AS ?count) WHERE {
      ?article wdt:P31 wd:Q13442814 .
      ?article wdt:P921 ?subject .
      ?subject wdt:P625 ?coord .
    }
    """
    result = query_wikidata(query, timeout=180, use_scholarly_endpoint=True)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def count_scholarly_articles_with_temporal_scope() -> Optional[int]:
    """
    Count scholarly articles with explicit temporal scope (P580/P582).
    This indicates the time period studied, not publication date.
    OPTIMAP exports use these for research period.
    Uses the scholarly-specific Wikidata endpoint for better performance.
    """
    query = """
    SELECT (COUNT(DISTINCT ?article) AS ?count) WHERE {
      ?article wdt:P31 wd:Q13442814 .
      { ?article wdt:P580 ?start . }
      UNION { ?article wdt:P582 ?end . }
    }
    """
    result = query_wikidata(query, timeout=120, use_scholarly_endpoint=True)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def count_scholarly_articles_with_start_time() -> Optional[int]:
    """Count scholarly articles with P580 (start time) for study period."""
    query = """
    SELECT (COUNT(?article) AS ?count) WHERE {
      ?article wdt:P31 wd:Q13442814 .
      ?article wdt:P580 ?start .
    }
    """
    result = query_wikidata(query, timeout=120, use_scholarly_endpoint=True)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def count_scholarly_articles_with_end_time() -> Optional[int]:
    """Count scholarly articles with P582 (end time) for study period."""
    query = """
    SELECT (COUNT(?article) AS ?count) WHERE {
      ?article wdt:P31 wd:Q13442814 .
      ?article wdt:P582 ?end .
    }
    """
    result = query_wikidata(query, timeout=120, use_scholarly_endpoint=True)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def get_scholarly_articles_with_coordinates_sample(limit: int = 50) -> List[Dict]:
    """
    Get sample of scholarly articles with direct coordinates.
    Useful to understand what types of articles have P625.
    """
    query = f"""
    SELECT ?article ?articleLabel ?coord ?journal ?journalLabel WHERE {{
      ?article wdt:P31 wd:Q13442814 .
      ?article wdt:P625 ?coord .
      OPTIONAL {{ ?article wdt:P1433 ?journal . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
    }}
    LIMIT {limit}
    """
    result = query_wikidata(query, timeout=120, use_scholarly_endpoint=True)
    if result and result.get("results", {}).get("bindings"):
        return result["results"]["bindings"]
    return []


def count_scholarly_articles_with_geoshape() -> Optional[int]:
    """
    Count scholarly articles with geoshape (P3896).
    P3896 stores GeoJSON polygon/line data via Wikimedia Commons Data namespace.
    This is an alternative to point coordinates for representing study areas.
    """
    query = """
    SELECT (COUNT(DISTINCT ?article) AS ?count) WHERE {
      ?article wdt:P31 wd:Q13442814 .
      ?article wdt:P3896 ?geoshape .
    }
    """
    result = query_wikidata(query, timeout=120, use_scholarly_endpoint=True)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def count_journal_articles_with_geoshape(journal_qid: str) -> Optional[int]:
    """
    Count articles from a journal that have geoshape (P3896).
    """
    query = f"""
    SELECT (COUNT(?article) AS ?count) WHERE {{
      ?article wdt:P1433 wd:{journal_qid} .
      ?article wdt:P3896 ?geoshape .
    }}
    """
    result = query_wikidata(query, timeout=60, use_scholarly_endpoint=True)
    if result and result.get("results", {}).get("bindings"):
        return int(result["results"]["bindings"][0]["count"]["value"])
    return None


def get_scholarly_articles_with_geoshape_sample(limit: int = 20) -> List[Dict]:
    """
    Get sample of scholarly articles with geoshape (P3896).
    Shows the GeoJSON file reference from Commons Data namespace.
    """
    query = f"""
    SELECT ?article ?articleLabel ?geoshape ?journal ?journalLabel WHERE {{
      ?article wdt:P31 wd:Q13442814 .
      ?article wdt:P3896 ?geoshape .
      OPTIONAL {{ ?article wdt:P1433 ?journal . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
    }}
    LIMIT {limit}
    """
    result = query_wikidata(query, timeout=120, use_scholarly_endpoint=True)
    if result and result.get("results", {}).get("bindings"):
        return result["results"]["bindings"]
    return []


def get_geographic_subject_distribution(limit: int = 20) -> List[Dict]:
    """
    Get distribution of geographic main subjects for scholarly articles.
    Shows which geographic entities are most commonly studied.
    Uses the scholarly-specific Wikidata endpoint.
    """
    query = f"""
    SELECT ?subject ?subjectLabel (COUNT(?article) AS ?count) WHERE {{
      ?article wdt:P31 wd:Q13442814 .
      ?article wdt:P921 ?subject .
      ?subject wdt:P625 ?coord .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
    }}
    GROUP BY ?subject ?subjectLabel
    ORDER BY DESC(?count)
    LIMIT {limit}
    """
    result = query_wikidata(query, timeout=180, use_scholarly_endpoint=True)
    if result and result.get("results", {}).get("bindings"):
        return result["results"]["bindings"]
    return []


def get_geospatial_metadata_summary() -> Dict[str, Any]:
    """
    Get comprehensive summary of geospatial metadata on scholarly works.
    Returns counts for different approaches to geographic annotation.
    All queries use the scholarly-specific Wikidata endpoint.
    """
    summary = {
        "query_timestamp": format_timestamp(),
        "direct_coordinates_p625": count_scholarly_articles_with_coordinates(),
        "bounding_box_p1332_p1335": count_scholarly_articles_with_bounding_box(),
        "geographic_main_subject": count_scholarly_articles_with_geographic_subject(),
        "temporal_scope_start_p580": count_scholarly_articles_with_start_time(),
        "temporal_scope_end_p582": count_scholarly_articles_with_end_time(),
    }
    return summary


def discover_partner_journals_wikidata() -> Dict[str, Any]:
    """
    Attempt to discover Wikidata QIDs for all collaboration partner journals.
    Returns a dict with journal names as keys and discovery results as values.
    """
    results = {}

    for journal in COLLABORATION_PARTNERS["journals"]:
        name = journal["name"]
        issn = journal.get("issn")

        result = {
            "name": name,
            "issn": issn,
            "wikidata_qid": None,
            "wikidata_label": None,
            "discovery_method": None
        }

        # Try ISSN lookup first (most reliable)
        if issn:
            wd_result = get_journal_by_issn(issn)
            if wd_result:
                qid = wd_result.get("item", {}).get("value", "").split("/")[-1]
                result["wikidata_qid"] = qid
                result["wikidata_label"] = wd_result.get("itemLabel", {}).get("value")
                result["discovery_method"] = "issn"

        # Fall back to name search if ISSN didn't work
        if not result["wikidata_qid"]:
            search_results = search_journal_wikidata(name.split("(")[0].strip())
            if search_results:
                # Take first result
                qid = search_results[0].get("item", {}).get("value", "").split("/")[-1]
                result["wikidata_qid"] = qid
                result["wikidata_label"] = search_results[0].get("itemLabel", {}).get("value")
                result["discovery_method"] = "name_search"

        results[name] = result
        time.sleep(0.5)  # Rate limiting

    return results


# =============================================================================
# Geometry Fetching for Visualization
# =============================================================================

def parse_wkt_point(wkt_point: str) -> Optional[tuple]:
    """
    Parse WKT Point string to (latitude, longitude) tuple.

    WKT format: "Point(longitude latitude)"
    Note: WKT uses (lon, lat), not (lat, lon)
    """
    import re
    match = re.match(r"Point\(([-\d.]+)\s+([-\d.]+)\)", wkt_point)
    if match:
        lon, lat = float(match.group(1)), float(match.group(2))
        return (lat, lon)
    return None


def fetch_commons_geoshape(data_page_title: str) -> Optional[Dict]:
    """
    Fetch GeoJSON from a Wikimedia Commons Data page.

    Args:
        data_page_title: Title with or without "Data:" prefix
                        (e.g., "Study_Area.map" or "Data:Study_Area.map")

    Returns:
        GeoJSON dict or None if fetch failed
    """
    # Clean up title
    if data_page_title.startswith("Data:"):
        data_page_title = data_page_title[5:]

    # Try direct raw access first
    raw_url = f"https://commons.wikimedia.org/wiki/Data:{data_page_title}?action=raw"

    try:
        response = requests.get(raw_url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # Commons Data files have structure: {"license": ..., "data": <geojson>}
            return data.get("data", data)
    except Exception as e:
        print(f"Failed to fetch geoshape {data_page_title}: {e}")

    return None


def get_all_scholarly_geometries(limit: int = 500) -> List[Dict]:
    """
    Fetch all scholarly articles with any geospatial property.

    Returns list of dicts with:
    - qid: Wikidata QID
    - label: Article title
    - geom_type: 'point', 'bbox', or 'geoshape'
    - geometry data (varies by type)
    """
    # Query for P625 (coordinates)
    query_p625 = f"""
    SELECT ?article ?articleLabel ?coord WHERE {{
      ?article wdt:P31 wd:Q13442814 .
      ?article wdt:P625 ?coord .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
    }}
    LIMIT {limit}
    """

    # Query for P1332-P1335 (bounding box)
    query_bbox = f"""
    SELECT ?article ?articleLabel ?north ?south ?east ?west WHERE {{
      ?article wdt:P31 wd:Q13442814 .
      ?article wdt:P1332 ?north .
      ?article wdt:P1333 ?south .
      ?article wdt:P1334 ?east .
      ?article wdt:P1335 ?west .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
    }}
    LIMIT {limit}
    """

    # Query for P3896 (geoshape)
    query_geoshape = f"""
    SELECT ?article ?articleLabel ?geoshape WHERE {{
      ?article wdt:P31 wd:Q13442814 .
      ?article wdt:P3896 ?geoshape .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
    }}
    LIMIT {limit}
    """

    results = []

    # Fetch P625 results
    p625_result = query_wikidata(query_p625, timeout=120, use_scholarly_endpoint=True)
    if p625_result and p625_result.get("results", {}).get("bindings"):
        for item in p625_result["results"]["bindings"]:
            qid = item.get("article", {}).get("value", "").split("/")[-1]
            label = item.get("articleLabel", {}).get("value", "Unknown")
            coord = item.get("coord", {}).get("value", "")

            parsed = parse_wkt_point(coord)
            if parsed:
                lat, lon = parsed
                results.append({
                    "qid": qid,
                    "label": label,
                    "geom_type": "point",
                    "lat": lat,
                    "lon": lon
                })

    # Fetch bbox results
    # Note: P1332-P1335 return WKT Point format, need to extract lat/lon appropriately
    bbox_result = query_wikidata(query_bbox, timeout=120, use_scholarly_endpoint=True)
    if bbox_result and bbox_result.get("results", {}).get("bindings"):
        for item in bbox_result["results"]["bindings"]:
            qid = item.get("article", {}).get("value", "").split("/")[-1]
            label = item.get("articleLabel", {}).get("value", "Unknown")

            try:
                # Parse WKT Points - extract lat from N/S points, lon from E/W points
                north_wkt = item.get("north", {}).get("value", "")
                south_wkt = item.get("south", {}).get("value", "")
                east_wkt = item.get("east", {}).get("value", "")
                west_wkt = item.get("west", {}).get("value", "")

                north_parsed = parse_wkt_point(north_wkt)
                south_parsed = parse_wkt_point(south_wkt)
                east_parsed = parse_wkt_point(east_wkt)
                west_parsed = parse_wkt_point(west_wkt)

                if all([north_parsed, south_parsed, east_parsed, west_parsed]):
                    # Extract: lat from N/S points, lon from E/W points
                    north = north_parsed[0]  # latitude
                    south = south_parsed[0]  # latitude
                    east = east_parsed[1]    # longitude (second element after swap)
                    west = west_parsed[1]    # longitude

                    results.append({
                        "qid": qid,
                        "label": label,
                        "geom_type": "bbox",
                        "north": north,
                        "south": south,
                        "east": east,
                        "west": west
                    })
            except (ValueError, TypeError, IndexError):
                continue

    # Fetch geoshape results
    geoshape_result = query_wikidata(query_geoshape, timeout=120, use_scholarly_endpoint=True)
    if geoshape_result and geoshape_result.get("results", {}).get("bindings"):
        for item in geoshape_result["results"]["bindings"]:
            qid = item.get("article", {}).get("value", "").split("/")[-1]
            label = item.get("articleLabel", {}).get("value", "Unknown")
            geoshape_uri = item.get("geoshape", {}).get("value", "")

            # Extract filename from URI
            if geoshape_uri:
                filename = geoshape_uri.split("/")[-1]
                if filename.startswith("Data:"):
                    filename = filename[5:]

                results.append({
                    "qid": qid,
                    "label": label,
                    "geom_type": "geoshape",
                    "geoshape_file": filename
                })

    return results


def create_geometry_geodataframe(geometries: List[Dict]) -> Any:
    """
    Convert geometry list to a GeoPandas GeoDataFrame.

    Requires geopandas and shapely to be installed.
    Returns None if dependencies not available.
    """
    try:
        import geopandas as gpd
        from shapely.geometry import Point, box, shape
    except ImportError:
        print("GeoPandas/Shapely not available")
        return None

    features = []

    for geom in geometries:
        geom_type = geom.get("geom_type")
        geometry = None

        if geom_type == "point":
            geometry = Point(geom["lon"], geom["lat"])

        elif geom_type == "bbox":
            geometry = box(
                geom["west"], geom["south"],
                geom["east"], geom["north"]
            )

        elif geom_type == "geoshape":
            geojson = fetch_commons_geoshape(geom.get("geoshape_file", ""))
            if geojson:
                try:
                    geometry = shape(geojson)
                except Exception:
                    continue

        if geometry:
            features.append({
                "qid": geom.get("qid"),
                "label": geom.get("label"),
                "geom_type": geom_type,
                "geometry": geometry
            })

    if not features:
        return gpd.GeoDataFrame(
            columns=["qid", "label", "geom_type", "geometry"],
            crs="EPSG:4326"
        )

    return gpd.GeoDataFrame(features, crs="EPSG:4326")


if __name__ == "__main__":
    # Quick test of the helper functions
    print("Testing Wikidata P1343 query...")
    count = count_p1343_scholarly_articles()
    print(f"Scholarly articles with P1343: {count}")

    print("\nTesting OpenCitations issues fetch...")
    issues = get_github_issues(per_page=5)
    print(f"Fetched {len(issues)} issues")

    for issue in issues[:3]:
        parsed = parse_opencitations_issue(issue)
        print(f"  - #{parsed['issue_number']}: {parsed['status']} by {parsed['creator']}")
