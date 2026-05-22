/**
 * Smart Travel Advisor — frontend logic
 *
 * Responsibilities:
 *  - Capture search input and call /api/travel
 *  - Manage loading / error / results UI states
 *  - Render each data section, degrading gracefully when a section has an error
 */

"use strict";

// ─── DOM refs ────────────────────────────────────────────────────────────────
const input       = document.getElementById("country-input");
const searchBtn   = document.getElementById("search-btn");
const stateIdle   = document.getElementById("state-idle");
const stateLoad   = document.getElementById("state-loading");
const stateError  = document.getElementById("state-error");
const stateResult = document.getElementById("state-results");
const errorText   = document.getElementById("error-msg-text");

// ─── State helpers ────────────────────────────────────────────────────────────
function showState(name) {
  [stateIdle, stateLoad, stateError, stateResult].forEach(el => (el.style.display = "none"));
  document.getElementById(`state-${name}`).style.display = "block";
}

function setLoading(on) {
  searchBtn.disabled = on;
  searchBtn.innerHTML = on
    ? '<span class="spinner-border spinner-border-sm" role="status"></span> Loading…'
    : '<i class="bi bi-search"></i> Explore';
}

// ─── Number formatting ───────────────────────────────────────────────────────
function formatPop(n) {
  if (n >= 1_000_000_000) return (n / 1_000_000_000).toFixed(2) + "B";
  if (n >= 1_000_000)     return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000)         return (n / 1_000).toFixed(0) + "K";
  return String(n);
}

// ─── Partial-error notice (shown inside a card when one API failed) ──────────
function partialError(msg) {
  return `<p class="partial-error"><i class="bi bi-exclamation-circle"></i>${escHtml(msg)}</p>`;
}

// ─── XSS guard: escape any string before inserting as HTML ───────────────────
function escHtml(str) {
  const d = document.createElement("div");
  d.textContent = String(str ?? "");
  return d.innerHTML;
}

// ─── Stat row builder ─────────────────────────────────────────────────────────
function statRow(label, value) {
  return `<div class="stat-row">
    <span class="stat-label">${escHtml(label)}</span>
    <span class="stat-value">${escHtml(String(value ?? "N/A"))}</span>
  </div>`;
}

// ─── Tag builder ─────────────────────────────────────────────────────────────
function tagList(items) {
  if (!items || !items.length) return `<span class="partial-error">No data.</span>`;
  return items.map(i => `<span class="tag">${escHtml(i)}</span>`).join("");
}

// ─── Renderers ───────────────────────────────────────────────────────────────

function renderCountryHeader(c) {
  document.getElementById("flag-img").src      = c.flag_url  || "";
  document.getElementById("flag-img").alt      = c.flag_alt  || "Flag";
  document.getElementById("country-name-title").textContent = c.name || "Unknown";
  document.getElementById("region-badge").textContent =
    [c.subregion, c.region].filter(Boolean).join(", ") || "";
}

function renderFacts(c) {
  const el = document.getElementById("facts-body");
  if (c.error) { el.innerHTML = partialError(c.error); return; }

  el.innerHTML =
    statRow("Official Name", c.official_name) +
    statRow("Capital",       c.capital) +
    statRow("Population",    formatPop(c.population)) +
    statRow("Region",        c.region) +
    statRow("Timezone(s)",   (c.timezones || []).join(", ")) +
    statRow("Domain",        c.tld);
}

function renderWeather(w) {
  const el = document.getElementById("weather-body");
  if (w.error) { el.innerHTML = partialError(w.error); return; }

  const iconUrl = w.icon
    ? `https://openweathermap.org/img/wn/${w.icon}@2x.png`
    : "";

  el.innerHTML = `
    <div class="weather-big">
      ${iconUrl ? `<img src="${escHtml(iconUrl)}" alt="${escHtml(w.description)}" />` : ""}
      <div>
        <div class="temp">${w.temperature != null ? Math.round(w.temperature) + "°C" : "N/A"}</div>
        <div class="desc">${escHtml(w.description)}</div>
      </div>
    </div>` +
    statRow("Feels Like",   w.feels_like  != null ? Math.round(w.feels_like)  + "°C" : "N/A") +
    statRow("Min / Max",    w.temp_min    != null ? `${Math.round(w.temp_min)}°C / ${Math.round(w.temp_max)}°C` : "N/A") +
    statRow("Humidity",     w.humidity    != null ? w.humidity + "%" : "N/A") +
    statRow("Wind Speed",   w.wind_speed  != null ? w.wind_speed + " m/s" : "N/A") +
    statRow("Visibility",   w.visibility  != null ? (w.visibility / 1000).toFixed(1) + " km" : "N/A");
}

function renderLanguages(c) {
  const el = document.getElementById("languages-body");
  el.innerHTML = c.error ? partialError(c.error) : tagList(c.languages);
}

function renderCurrencies(c) {
  const el = document.getElementById("currencies-body");
  el.innerHTML = c.error ? partialError(c.error) : tagList(c.currencies);
}

function renderWiki(w) {
  const el = document.getElementById("wiki-body");
  if (w.error) { el.innerHTML = partialError(w.error); return; }

  let html = "";

  if (w.tourism) {
    html += `<div class="wiki-section">
      <div class="wiki-section-label">Tourism &amp; Attractions</div>
      <p class="wiki-text">${escHtml(w.tourism)}</p>
    </div>`;
  }
  if (w.cuisine) {
    html += `<div class="wiki-section">
      <div class="wiki-section-label">Food &amp; Cuisine</div>
      <p class="wiki-text">${escHtml(w.cuisine)}</p>
    </div>`;
  }

  el.innerHTML = html || partialError("No Wikipedia content available.");
}

// ─── Main search handler ──────────────────────────────────────────────────────
async function doSearch() {
  const query = input.value.trim();

  // Client-side empty check before even hitting the server.
  if (!query) {
    input.focus();
    input.classList.add("is-invalid");
    setTimeout(() => input.classList.remove("is-invalid"), 1500);
    return;
  }

  showState("loading");
  setLoading(true);

  try {
    const res = await fetch(`/api/travel?country=${encodeURIComponent(query)}`);
    const data = await res.json();

    // 400 means bad user input; surface the server's message.
    if (!res.ok) {
      errorText.textContent = data.error || "Invalid request.";
      showState("error");
      return;
    }

    // Render each section independently — partial failures are shown inside cards.
    renderCountryHeader(data.country.error ? {} : data.country);
    renderFacts(data.country);
    renderWeather(data.weather);
    renderLanguages(data.country);
    renderCurrencies(data.country);
    renderWiki(data.wiki);

    showState("results");

  } catch (err) {
    // Network-level failure (offline, DNS failure, etc.)
    errorText.textContent = "Could not reach the server. Check your connection.";
    showState("error");
  } finally {
    setLoading(false);
  }
}

// ─── Event listeners ──────────────────────────────────────────────────────────
searchBtn.addEventListener("click", doSearch);

// Allow Enter key in the search box.
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") doSearch();
});
