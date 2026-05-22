from app.utils import safe_get

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(capital: str, api_key: str) -> dict:
    """
    Fetches current weather for a capital city from OpenWeatherMap.

    Returns a clean dict or an error dict.
    Uses metric units (Celsius) by default.
    """
    # Guard: if no API key is configured at all, return a friendly message
    # instead of sending a guaranteed-to-fail request.
    if not api_key:
        return {"error": "OpenWeather API key is not configured. Add it to your .env file."}

    if not capital or capital == "N/A":
        return {"error": "No capital city available to fetch weather for."}

    result = safe_get(
        BASE_URL,
        params={
            "q": capital,
            "appid": api_key,
            "units": "metric",
        },
    )

    if not result["ok"]:
        return {"error": result["error"]}

    data = result["data"]

    # Safely extract nested values with sensible fallbacks so a missing field
    # from the API never causes a KeyError.
    main = data.get("main", {})
    wind = data.get("wind", {})
    weather_list = data.get("weather", [{}])
    weather_desc = weather_list[0] if weather_list else {}

    return {
        "city": data.get("name", capital),
        "temperature": main.get("temp"),
        "feels_like": main.get("feels_like"),
        "temp_min": main.get("temp_min"),
        "temp_max": main.get("temp_max"),
        "humidity": main.get("humidity"),
        "description": weather_desc.get("description", "N/A").capitalize(),
        "icon": weather_desc.get("icon", ""),
        "wind_speed": wind.get("speed"),
        "visibility": data.get("visibility"),
    }
