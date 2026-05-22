from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Blueprint, jsonify, render_template, request, current_app
from app.utils import sanitize_country
from app.services.countries import get_country_info
from app.services.weather import get_weather
from app.services.wikipedia import get_wiki_info

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@main.route("/api/travel")
def travel():
    """
    Main aggregation endpoint.

    Query param: ?country=<name>

    Validates input, then fires all three service calls concurrently using a
    ThreadPoolExecutor. Each service is independent — if one fails, the others
    still return their data. The frontend handles partial failures gracefully.

    Returns JSON:
    {
        "country": { ... } | { "error": "..." },
        "weather":  { ... } | { "error": "..." },
        "wiki":     { ... } | { "error": "..." }
    }
    """
    raw_input = request.args.get("country", "")

    # --- Input validation (before any network call) ---
    is_valid, result = sanitize_country(raw_input)
    if not is_valid:
        # Return 400 so the frontend can distinguish a user error from a server error.
        return jsonify({"error": result}), 400

    country_name = result
    api_key = current_app.config.get("OPENWEATHER_API_KEY", "")

    # --- Concurrent API calls ---
    # We define small lambdas here because ThreadPoolExecutor.submit() needs callables.
    # Country info is fetched first (synchronously, fast) because we need the capital
    # city name before we can call the weather API.
    country_data = get_country_info(country_name)

    # Determine capital for the weather call (may be "N/A" if the country API failed).
    capital = country_data.get("capital", "N/A") if "error" not in country_data else "N/A"

    # Now run weather + Wikipedia concurrently since they are independent.
    tasks = {
        "weather": lambda: get_weather(capital, api_key),
        "wiki": lambda: get_wiki_info(country_name),
    }

    results = {}
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_key = {executor.submit(fn): key for key, fn in tasks.items()}
        for future in as_completed(future_to_key):
            key = future_to_key[future]
            try:
                results[key] = future.result()
            except Exception as exc:
                # Catch any unexpected exception from a service so it never
                # propagates and kills the entire response.
                results[key] = {"error": f"Unexpected error: {str(exc)}"}

    return jsonify(
        {
            "country": country_data,
            "weather": results.get("weather", {"error": "Weather data unavailable."}),
            "wiki": results.get("wiki", {"error": "Wikipedia data unavailable."}),
        }
    )
