from app.utils import safe_get

BASE_URL = "https://en.wikipedia.org/w/api.php"

# Topics to search for, in order. We try each and take the first useful result.
TOPICS = [
    "{country} tourism",
    "{country} tourist attractions",
    "{country} cuisine",
    "{country} culture",
]


def _fetch_summary(search_term: str) -> str | None:
    """
    Searches Wikipedia for search_term and returns a short plain-text extract,
    or None if nothing useful is found.
    """
    # Step 1: search for the best matching page title.
    search_result = safe_get(
        BASE_URL,
        params={
            "action": "query",
            "list": "search",
            "srsearch": search_term,
            "format": "json",
            "srlimit": 1,
        },
    )

    if not search_result["ok"]:
        return None

    hits = search_result["data"].get("query", {}).get("search", [])
    if not hits:
        return None

    page_title = hits[0]["title"]

    # Step 2: fetch a short plain-text extract for that page title.
    extract_result = safe_get(
        BASE_URL,
        params={
            "action": "query",
            "prop": "extracts",
            "exintro": True,        # Only the introductory section
            "explaintext": True,    # Plain text, no HTML markup
            "titles": page_title,
            "format": "json",
            "exsentences": 5,       # Limit to 5 sentences
        },
    )

    if not extract_result["ok"]:
        return None

    pages = extract_result["data"].get("query", {}).get("pages", {})
    # The page dict is keyed by page ID (a string number, or "-1" if missing).
    for page_id, page in pages.items():
        if page_id == "-1":
            return None
        extract = page.get("extract", "").strip()
        if extract:
            return extract

    return None


def get_wiki_info(country_name: str) -> dict:
    """
    Collects Wikipedia summaries for tourism and cuisine for the given country.
    Each topic is attempted independently so a failure on one doesn't kill the rest.
    """
    topics = {
        "tourism": [
            f"{country_name} tourism",
            f"{country_name} tourist attractions",
        ],
        "cuisine": [
            f"{country_name} cuisine",
            f"{country_name} food",
        ],
    }

    results = {}

    for category, search_terms in topics.items():
        for term in search_terms:
            summary = _fetch_summary(term)
            if summary:
                results[category] = summary
                break  # Got a useful result; no need to try the fallback term.
        else:
            # Both search terms yielded nothing.
            results[category] = None

    if not any(results.values()):
        return {"error": f"No Wikipedia information found for '{country_name}'."}

    return results
