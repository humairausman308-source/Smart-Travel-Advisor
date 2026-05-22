# ANSWERS.md

---

## 1. How to run

**Requirements:** Python 3.11+, a free OpenWeatherMap API key.

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd smart-travel-advisor

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your environment file
cp .env.example .env
# Edit .env — replace the placeholder with your real OpenWeatherMap key

# 5. Run
python run.py
```

Open [http://localhost:5000](http://localhost:5000). No database, no build step, no Docker needed.

---

## 2. Stack choice

**Why Python + Flask + plain HTML/Bootstrap?**

- **Python** has excellent HTTP libraries (`requests`) and a simple concurrency model (`ThreadPoolExecutor`) that fits this use case perfectly — parallel API calls without the complexity of async/await.
- **Flask** is the lightest web framework that still gives you routing, templating, and a development server. No ORM needed, no overhead.
- **Bootstrap 5 + vanilla JS** keeps the frontend dependency-free. No build pipeline, no `node_modules`, no bundler — just open the file and it works. This makes the project trivially runnable on any machine.
- **python-dotenv** is the standard zero-config approach to environment variable management in Python.

**What would have been a worse choice?**

Using **Next.js** (React) for this project would have been overkill and actively worse:

- Would require Node.js, npm, and a build step just to run "hello world"
- The OpenWeather API key would need to be handled via server-side API routes to stay secure — added indirection for no benefit
- A fresh-machine setup would involve `npm install` (hundreds of packages, minutes of download) vs `pip install -r requirements.txt` (3 packages, seconds)
- The app has no client-side state management, no routing, no component reuse — all the things React is designed for are absent here

---

## 3. One real edge case

**Edge case: The REST Countries API returns 404 for an unrecognised country name**

**File:** `app/utils.py`, lines 24–28

```python
if response.status_code == 404:
    return {"ok": False, "error": "Not found (404) — check the name and try again."}
```

**What happens:** When the user types something like `"Freedonia"` or `"Abc123"`, the REST Countries API responds with HTTP 404 and an HTML error page — not JSON. Without this explicit check, the code would fall through to `response.json()`, which raises a `JSONDecodeError` (because HTML is not valid JSON). That would be caught by the generic `ValueError` handler below, but the error message ("Received an unreadable response") would be confusing and misleading.

With this handling, the user sees: *"Not found (404) — check the name and try again."* — which is accurate and actionable.

The input validator in `sanitize_country()` (`app/utils.py`, lines 48–65) also catches obviously bad inputs (empty strings, inputs with digits, inputs over 100 characters) before any network call is made at all, saving API quota.

---

## 4. AI usage

AI (Claude) was used throughout this project:

| Area | How AI was used |
|------|----------------|
| Architecture | Proposed the backend-proxy pattern, concurrent API calls, and per-section error isolation |
| `app/utils.py` | Generated the initial `safe_get()` wrapper and `sanitize_country()` validator |
| `app/services/wikipedia.py` | Generated the two-step search → extract flow |
| `app/routes.py` | Generated the `ThreadPoolExecutor` pattern for concurrent calls |
| `templates/index.html` + `static/app.js` | Generated the UI layout and rendering logic |
| `ANSWERS.md` | Drafted the structure; content was written manually |

**What was changed from the AI output and why:**

The original `wikipedia.py` used a single search query per topic (e.g. `"France tourism"`). The AI output did not handle the case where that specific query returned no useful Wikipedia article — it just returned `None` without a fallback.

I changed it to a **two-term fallback list** per topic (e.g. try `"France tourism"` first, then `"France tourist attractions"` if the first returns nothing). This was added in the `for term in search_terms` loop in `get_wiki_info()`. The reason: Wikipedia's search API is fuzzy — some country names pair better with "cuisine" and others with "food", or "tourism" vs "tourist attractions". Without the fallback, countries like smaller island nations would frequently show no Wikipedia content at all.

---

## 5. Honest gap

**What isn't good enough: no caching**

Every search hits all three external APIs fresh, every time. If a user searches "Japan" twice in a row, six identical HTTP requests are made.

**How it would be improved with another day of work:**

Add a simple server-side cache using Flask-Caching with a Redis or in-memory backend:

```python
from flask_caching import Cache
cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 600})

@cache.memoize(600)  # cache for 10 minutes
def get_country_info(country_name): ...
```

Ten minutes is a sensible TTL because country facts never change and weather changes slowly. This would:
- Dramatically reduce response times for repeated queries
- Protect against hitting OpenWeatherMap's free-tier rate limit (60 calls/minute)
- Make the app usable under modest concurrent load

A production version would also add rate-limiting on the `/api/travel` endpoint itself (e.g. via Flask-Limiter) to prevent abuse.
