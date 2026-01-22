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
GITHUB_API_BASE = "https://api.github.com"
OPENCITATIONS_REPO = "opencitations/crowdsourcing"

# Known KOMET contributors (GitHub handles)
# Add more handles as team members are identified
KOMET_CONTRIBUTORS = [
    "GaziYucel",  # Gazi Yuecel, TIB - OPTIMETA/KOMET developer
    # Add more KOMET team GitHub handles here
]

# User-Agent for API requests (required by Wikidata)
HEADERS = {
    "User-Agent": "KOMET-Report/1.0 (https://projects.tib.eu/komet; mailto:daniel.nuest@tu-dresden.de)",
    "Accept": "application/sparql-results+json"
}

# Timeline log file for tracking statistics over time
TIMELINE_LOG_FILE = "komet_timeline.json"

# =============================================================================
# OPTIMETA/KOMET Collaboration Partners
# Source: https://projects.tib.eu/optimeta/en/
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

def query_wikidata(sparql_query: str, timeout: int = 60) -> Optional[Dict]:
    """
    Execute a SPARQL query against the Wikidata Query Service.

    Args:
        sparql_query: The SPARQL query string
        timeout: Request timeout in seconds

    Returns:
        JSON response as dict, or None if query fails
    """
    try:
        response = requests.get(
            WIKIDATA_SPARQL_ENDPOINT,
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
    Search for Wikidata items that reference KOMET or OPTIMETA as source.
    Checks P1343 values for mentions of these projects.
    """
    query = """
    SELECT ?item ?itemLabel ?source ?sourceLabel WHERE {
      ?item wdt:P1343 ?source .
      ?source rdfs:label ?sourceLabel .
      FILTER(CONTAINS(LCASE(?sourceLabel), "komet") || CONTAINS(LCASE(?sourceLabel), "optimeta"))
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
    }
    LIMIT 100
    """
    result = query_wikidata(query, timeout=60)
    if result and result.get("results", {}).get("bindings"):
        return result["results"]["bindings"]
    return []


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


# =============================================================================
# Timeline Logging Functions
# =============================================================================

def load_timeline(filepath: str = TIMELINE_LOG_FILE) -> Dict[str, Any]:
    """
    Load the timeline log file. Creates empty structure if not exists.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "created": format_timestamp(),
            "last_updated": None,
            "observations": []
        }


def save_timeline(timeline: Dict[str, Any], filepath: str = TIMELINE_LOG_FILE) -> None:
    """
    Save the timeline log file.
    """
    timeline["last_updated"] = format_timestamp()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False, default=str)


def add_observation(
    timeline: Dict[str, Any],
    metric_name: str,
    value: Any,
    source: str,
    notes: Optional[str] = None
) -> bool:
    """
    Add an observation to the timeline.

    Only adds a new entry if the value has changed from the last observation
    for this metric. If value is the same, updates the timestamp of the
    existing observation.

    Args:
        timeline: The timeline dict to update
        metric_name: Name of the metric (e.g., "wikidata_p1343_count")
        value: The observed value
        source: Data source (e.g., "wikidata", "opencitations")
        notes: Optional notes about this observation

    Returns:
        True if a new entry was added, False if only timestamp updated
    """
    timestamp = format_timestamp()

    # Find the most recent observation for this metric
    recent = None
    for obs in reversed(timeline["observations"]):
        if obs["metric"] == metric_name:
            recent = obs
            break

    if recent and recent["value"] == value:
        # Value unchanged - just update the timestamp
        recent["last_seen"] = timestamp
        return False
    else:
        # New value - add new observation
        observation = {
            "timestamp": timestamp,
            "last_seen": timestamp,
            "metric": metric_name,
            "value": value,
            "source": source
        }
        if notes:
            observation["notes"] = notes
        timeline["observations"].append(observation)
        return True


def get_metric_history(timeline: Dict[str, Any], metric_name: str) -> List[Dict]:
    """
    Get all observations for a specific metric.
    """
    return [
        obs for obs in timeline["observations"]
        if obs["metric"] == metric_name
    ]


def get_latest_metrics(timeline: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get the most recent value for each metric.
    """
    latest = {}
    for obs in timeline["observations"]:
        metric = obs["metric"]
        if metric not in latest or obs["timestamp"] > latest[metric]["timestamp"]:
            latest[metric] = obs
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
