# Smart Travel Advisor

A full-stack web app that combines three public APIs to give you instant travel insights for any country — weather, facts, tourism, and local cuisine.

---

## Quick Start (single command after setup)

```bash
python run.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Prerequisites

- Python 3.11 or higher
- A free [OpenWeatherMap API key](https://openweathermap.org/api) (takes ~2 minutes to get)

---

## Setup Steps

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd smart-travel-advisor
```

### 2. Create and activate a virtual environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and replace `your_openweather_api_key_here` with your real key:

```
OPENWEATHER_API_KEY=abc123yourrealkey
```

### 5. Run the app

```bash
python run.py
```

Visit [http://localhost:5000](http://localhost:5000).

---

## APIs Used

| API | Purpose | Key required? |
|-----|---------|---------------|
| [REST Countries](https://restcountries.com) | Capital, population, currency, languages | No |
| [OpenWeatherMap](https://openweathermap.org/api) | Current weather for capital city | **Yes** (free) |
| [Wikipedia](https://www.mediawiki.org/wiki/API:Main_page) | Tourism & cuisine descriptions | No |

---

## Project Structure

```
smart-travel-advisor/
├── app/
│   ├── __init__.py         # Flask app factory
│   ├── routes.py           # API endpoints
│   ├── utils.py            # HTTP helper + input validation
│   └── services/
│       ├── countries.py    # REST Countries client
│       ├── weather.py      # OpenWeather client
│       └── wikipedia.py    # Wikipedia client
├── templates/
│   └── index.html          # Single-page UI
├── static/
│   └── app.js              # Frontend JS
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py
├── README.md
└── ANSWERS.md
```

---

## Features

- Search any country by name
- Live weather for the capital city
- Country facts (population, region, timezone, TLD)
- Languages and currencies displayed as tags
- Wikipedia summaries for tourism and local cuisine
- Graceful partial failures — if one API is slow or down, the rest still render
- Input validation with friendly error messages
- 5-second timeout per API call with user-friendly timeout messages
