import re
from app.utils import safe_get

WIKI_API = "https://en.wikipedia.org/w/api.php"

# HIGH-YIELD HUB: Guarantees specific, beautiful highlights instantly for major destinations
GLOBAL_CULTURE_MAP = {
    "Pakistan": {
        "tourism": [
            "The breathtaking Hunza Valley and Skardu in Gilgit-Baltistan, famous for soaring mountain peaks and alpine lakes.",
            "The lush green meadows of the Swat Valley, historic archaeological ruins, and alpine hill stations.",
            "Historical architectural landmarks including the majestic Badshahi Mosque and the ancient Lahore Fort."
        ],
        "cuisine": [
            "Aromatic Biryani and Pulao, which are celebratory, spiced rice dishes layered with marinated meats.",
            "Rich and slow-cooked meat delicacies like Nihari, Haleem, and freshly grilled Seekh Kebabs.",
            "Popular local street foods and snacks including crispy Samosas, Pakoras, and flaky parathas."
        ]
    },
    "Japan": {
        "tourism": [
            "The iconic Mount Fuji, historic temples in Kyoto, and the bustling, neon-lit districts of Tokyo.",
            "Beautiful coastal shrines like Itsukushima and the historic peace memorials in Hiroshima.",
            "The pristine nature trails, hot springs (Onsen), and cherry blossom parks across Hokkaido."
        ],
        "cuisine": [
            "Freshly prepared Sushi and Sashimi highlighting delicate traditional seafood cutting techniques.",
            "Rich, comforting bowls of Ramen noodles served in deeply savory, hours-long simmered broths.",
            "Crispy Tempura seafood, savory Okonomiyaki pancakes, and traditional matcha green tea sweets."
        ]
    }
}

def _fetch_safe_extract(search_term: str) -> str | None:
    """Fetches a tightly constrained, small text extract to prevent API/safe_get memory drops."""
    search_result = safe_get(
        WIKI_API,
        params={
            "action": "query",
            "list": "search",
            "srsearch": search_term,
            "format": "json",
            "srlimit": 1,
        },
    )

    if not search_result or not search_result.get("ok"):
        return None

    hits = search_result.get("data", {}).get("query", {}).get("search", [])
    if not hits:
        return None

    page_title = hits[0]["title"]
    
    # Requesting ONLY 3 sentences ensures safe_get will never hit a payload wall
    extract_result = safe_get(
        WIKI_API,
        params={
            "action": "query",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": page_title,
            "format": "json",
            "exsentences": 3, 
        },
    )

    if not extract_result or not extract_result.get("ok"):
        return None

    pages = extract_result.get("data", {}).get("query", {}).get("pages", {})
    for page_id, page in pages.items():
        if page_id != "-1":
            return page.get("extract", "").strip()
            
    return None


def format_dynamic_fallback(text: str) -> str:
    """Converts standard raw text paragraphs neatly into bullet points."""
    if not text:
        return "• Discover historic landmarks, scenic landscapes, and cultural heritage sites across the region."
    
    text = re.sub(r'\[\d+\]|\[.*?\]', '', text)
    text = re.sub(r'\s*\([^)]*\)', '', text)
    
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
    bullets = [f"• {s}." for s in sentences[:3]]
    
    return "\n".join(bullets)


def get_wiki_info(country_name: str) -> dict:
    """
    Main controller. Uses premium curated data blocks for popular destinations, 
    and handles global fallback dynamically through safe, lightweight API requests.
    """
    # Clean the input name
    country = country_name.strip()
    # Normalize capitalization (handles 'pakistan' -> 'Pakistan')
    lookup_name = country.title() 

    # FAST ROUTE: Look for premium matches first
    if lookup_name in GLOBAL_CULTURE_MAP:
        t_bullets = "\n".join([f"• {b}" for b in GLOBAL_CULTURE_MAP[lookup_name]["tourism"]])
        c_bullets = "\n".join([f"• {b}" for b in GLOBAL_CULTURE_MAP[lookup_name]["cuisine"]])
        
        return {
            "tourism": f" 🗺️ Must-Visit Spots & Attractions\n{t_bullets}",
            "cuisine": f" 🍲 Famous Culinary Delights\n{c_bullets}"
        }

    # SLOW DYNAMIC ROUTE: Fallback for any other country globally
    raw_tourism = _fetch_safe_extract(f"Tourist attractions in {lookup_name}") or _fetch_safe_extract(f"Tourism in {lookup_name}")
    raw_cuisine = _fetch_safe_extract(f"{lookup_name} cuisine") or _fetch_safe_extract(f"Cuisine of {lookup_name}")

    return {
        "tourism": f" 🗺️ Must-Visit Spots & Attractions\n{format_dynamic_fallback(raw_tourism)}",
        "cuisine": f" 🍲 Famous Culinary Delights\n{format_dynamic_fallback(raw_cuisine)}"
    }