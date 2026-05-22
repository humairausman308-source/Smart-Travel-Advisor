import requests
import difflib

REQUEST_TIMEOUT = 5

# Full country name list for fuzzy matching (no API call needed)
COUNTRY_NAMES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Argentina",
    "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain",
    "Bangladesh", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia",
    "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria",
    "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada",
    "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros",
    "Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic",
    "Denmark", "Djibouti", "Dominican Republic", "Ecuador", "Egypt",
    "El Salvador", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji",
    "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana",
    "Greece", "Guatemala", "Guinea", "Guyana", "Haiti", "Honduras", "Hungary",
    "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel",
    "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kuwait",
    "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya",
    "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi",
    "Malaysia", "Maldives", "Mali", "Malta", "Mauritania", "Mauritius",
    "Mexico", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco",
    "Mozambique", "Myanmar", "Namibia", "Nepal", "Netherlands", "New Zealand",
    "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway",
    "Oman", "Pakistan", "Palestine", "Panama", "Papua New Guinea", "Paraguay",
    "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia",
    "Rwanda", "Saudi Arabia", "Senegal", "Serbia", "Sierra Leone", "Singapore",
    "Slovakia", "Slovenia", "Somalia", "South Africa", "South Korea",
    "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden",
    "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand",
    "Togo", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan",
    "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom",
    "United States", "Uruguay", "Uzbekistan", "Venezuela", "Vietnam",
    "Yemen", "Zambia", "Zimbabwe",
]


def suggest_country(name: str) -> str | None:
    """
    Returns the closest matching country name for a misspelled input,
    or None if no close match is found.
    Uses difflib which is built into Python — no extra library needed.
    """
    matches = difflib.get_close_matches(
        name.strip().title(),   # normalise capitalisation before comparing
        COUNTRY_NAMES,
        n=1,
        cutoff=0.6              # 0.6 = must be at least 60% similar
    )
    return matches[0] if matches else None


def safe_get(url: str, params: dict = None, timeout: int = REQUEST_TIMEOUT) -> dict:
    try:
        response = requests.get(url, params=params, timeout=timeout)

        if not response.ok:
            if response.status_code == 404:
                return {"ok": False, "error": "not_found"}
            return {"ok": False, "error": f"API returned status {response.status_code}."}

        return {"ok": True, "data": response.json()}

    except requests.exceptions.Timeout:
        return {"ok": False, "error": "The request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"ok": False, "error": "Could not reach the service. Check your internet connection."}
    except requests.exceptions.RequestException as exc:
        return {"ok": False, "error": f"Request failed: {str(exc)}"}
    except ValueError:
        return {"ok": False, "error": "Received an unreadable response from the API."}


def sanitize_country(name: str) -> tuple[bool, str]:
    cleaned = name.strip()

    if not cleaned:
        return False, "Please enter a country name."

    if len(cleaned) > 100:
        return False, "Input is too long. Please enter a valid country name."

    if any(char.isdigit() for char in cleaned):
        return False, "Country names don't contain numbers. Please check your input."

    return True, cleaned