import requests


REQUEST_TIMEOUT = 5  # seconds — prevents slow APIs from hanging the whole request


def safe_get(url: str, params: dict = None, timeout: int = REQUEST_TIMEOUT) -> dict:
    """
    Performs a GET request and returns a normalised result dict.

    Always returns a dict with either:
        {"ok": True,  "data": <parsed JSON>}
        {"ok": False, "error": <human-readable message>}

    This means callers never have to catch exceptions themselves — they just
    check result["ok"] before using result["data"].
    """
    try:
        response = requests.get(url, params=params, timeout=timeout)

        # Treat any non-2xx status as an error so callers don't have to check
        # status codes; just check result["ok"].
        if not response.ok:
            # Edge case: 404 from REST Countries when the country name is wrong.
            # Without this branch the code would try to call response.json() on
            # an HTML error page and raise a JSONDecodeError instead of returning
            # a clean message. (ANSWERS.md references app/utils.py line ~25)
            if response.status_code == 404:
                return {"ok": False, "error": "Not found (404) — check the name and try again."}
            return {
                "ok": False,
                "error": f"API returned status {response.status_code}.",
            }

        return {"ok": True, "data": response.json()}

    except requests.exceptions.Timeout:
        return {
            "ok": False,
            "error": "The request timed out. The service may be slow — please try again.",
        }
    except requests.exceptions.ConnectionError:
        return {
            "ok": False,
            "error": "Could not reach the service. Check your internet connection.",
        }
    except requests.exceptions.RequestException as exc:
        return {"ok": False, "error": f"Request failed: {str(exc)}"}
    except ValueError:
        # requests raises ValueError (JSONDecodeError is a subclass) when the
        # response body is not valid JSON.
        return {"ok": False, "error": "Received an unreadable response from the API."}


def sanitize_country(name: str) -> tuple[bool, str]:
    """
    Validates and cleans raw user input before it is sent to any external API.

    Returns (is_valid, cleaned_name_or_error_message).

    Checks performed:
    - Empty / whitespace-only string
    - Exceeds reasonable length (protects against absurdly long inputs)
    - Contains digits (country names don't have numbers)
    """
    cleaned = name.strip()

    if not cleaned:
        return False, "Please enter a country name."

    # Guard against inputs like 500-character strings sent by bots or bad actors.
    if len(cleaned) > 100:
        return False, "Input is too long. Please enter a valid country name."

    # Country names never contain digits; reject immediately.
    if any(char.isdigit() for char in cleaned):
        return False, "Country names don't contain numbers. Please check your input."

    return True, cleaned
