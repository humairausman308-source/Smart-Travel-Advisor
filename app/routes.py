from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Blueprint, jsonify, render_template, request, current_app
from app.utils import sanitize_country, suggest_country
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
    raw_input = request.args.get("country", "")

    is_valid, result = sanitize_country(raw_input)
    if not is_valid:
        return jsonify({"error": result}), 400

    country_name = result

    # Try fetching country data first
    country_data = get_country_info(country_name)

    # If country not found, try to suggest a correction
    if "error" in country_data:
        suggestion = suggest_country(country_name)
        if suggestion:
            return jsonify({
                "error": f'Country "{country_name}" not found.',
                "suggestion": suggestion
            }), 404
        else:
            return jsonify({
                "error": f'Country "{country_name}" not found. Please check the spelling and try again.'
            }), 404

    capital = country_data.get("capital", "N/A")
    api_key = current_app.config.get("OPENWEATHER_API_KEY", "")

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
                results[key] = {"error": f"Unexpected error: {str(exc)}"}

    return jsonify({
        "country": country_data,
        "weather": results.get("weather", {"error": "Weather data unavailable."}),
        "wiki": results.get("wiki", {"error": "Wikipedia data unavailable."}),
    })