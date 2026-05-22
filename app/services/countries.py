from app.utils import safe_get

BASE_URL = "https://restcountries.com/v3.1"


def get_country_info(country_name: str) -> dict:
    """
    Fetches structured country data from the REST Countries API.

    Returns a clean dict with the fields the frontend needs, or an error dict.
    Requesting only the specific fields we use (via the `fields` param) keeps
    the response payload small and fast.
    """
    result = safe_get(
        f"{BASE_URL}/name/{country_name}",
        params={
            "fields": "name,capital,population,currencies,languages,flags,region,subregion,timezones,tlds"
        },
    )

    if not result["ok"]:
        return {"error": result["error"]}

    # The API returns a list; take the first (best) match.
    raw = result["data"]
    if not raw:
        return {"error": "No country data returned."}

    country = raw[0]

    # --- Currency: the API returns a dict keyed by currency code ---
    currencies_raw = country.get("currencies", {})
    currencies = [
        f"{info.get('name', code)} ({info.get('symbol', '')})"
        for code, info in currencies_raw.items()
    ]

    # --- Languages: the API returns a dict keyed by language code ---
    languages = list(country.get("languages", {}).values())

    # --- Capital: stored as a list, may be empty for some territories ---
    capital_list = country.get("capital", [])
    capital = capital_list[0] if capital_list else "N/A"

    # --- Top-level domain ---
    tlds = country.get("tlds", [])
    tld = tlds[0] if tlds else "N/A"

    return {
        "name": country["name"]["common"],
        "official_name": country["name"].get("official", country["name"]["common"]),
        "capital": capital,
        "population": country.get("population", 0),
        "region": country.get("region", "N/A"),
        "subregion": country.get("subregion", "N/A"),
        "currencies": currencies,
        "languages": languages,
        "flag_url": country.get("flags", {}).get("svg", ""),
        "flag_alt": country.get("flags", {}).get("alt", "National flag"),
        "timezones": country.get("timezones", []),
        "tld": tld,
    }
