import re
from app.utils import safe_get

WIKI_API  = "https://en.wikipedia.org/w/api.php"
WIKI_REST = "https://en.wikipedia.org/api/rest_v1/page/summary"

# Hardcoded high-quality data for top destinations as guaranteed fallback.
# Wikipedia API results vary wildly by country — this ensures every major
# country always shows real, accurate, useful travel info.
COUNTRY_TRAVEL_DATA = {
    "pakistan": {
        "tourism": [
            "Badshahi Mosque and Lahore Fort — iconic Mughal-era landmarks in the heart of Lahore.",
            "Hunza Valley and Skardu in Gilgit-Baltistan, famous for dramatic mountain peaks and turquoise lakes.",
            "Mohenjo-daro — one of the world's oldest civilizations, a UNESCO World Heritage Site in Sindh.",
            "The ancient walled city of Peshawar and the historic Khyber Pass near the Afghan border.",
            "Fairy Meadows — a breathtaking grassland at the base of Nanga Parbat, the world's 9th highest peak.",
        ],
        "cuisine": [
            "Biryani and Pulao — fragrant spiced rice dishes layered with marinated meat, served at every celebration.",
            "Nihari and Haleem — slow-cooked meat stews, a beloved breakfast tradition in Lahore and Karachi.",
            "Seekh Kebabs and Chapli Kebabs — grilled minced meat specialties from the streets of Peshawar.",
            "Samosas, Pakoras, and Gol Gappay — iconic street snacks found at every corner across Pakistan.",
            "Karahi and Sajji — hearty meat dishes cooked in woks or slow-roasted whole, unique to Pakistani cuisine.",
        ],
    },
    "india": {
        "tourism": [
            "Taj Mahal in Agra — a UNESCO World Heritage Site and one of the Seven Wonders of the World.",
            "Jaipur's Amber Fort, Hawa Mahal, and City Palace — the Pink City's royal Rajput architecture.",
            "Kerala's backwaters — a serene network of lagoons, lakes, and canals along the Malabar Coast.",
            "Varanasi — one of the world's oldest living cities, with ancient ghats along the sacred Ganges River.",
            "Goa's beaches, Portuguese colonial churches, and vibrant nightlife along the Arabian Sea coast.",
        ],
        "cuisine": [
            "Butter Chicken and Dal Makhani — creamy, slow-cooked North Indian classics loved worldwide.",
            "Biryani — fragrant layered rice with spiced meat, with famous regional versions from Hyderabad and Lucknow.",
            "Dosa and Idli — crispy rice crepes and steamed cakes from South India, served with coconut chutney.",
            "Chaat and Pani Puri — explosive street food snacks bursting with tangy tamarind and spiced water.",
            "Rogan Josh and Dum Aloo — rich, slow-cooked Kashmiri specialties with aromatic whole spices.",
        ],
    },
    "turkey": {
        "tourism": [
            "Hagia Sophia and the Blue Mosque — awe-inspiring Byzantine and Ottoman masterpieces in Istanbul.",
            "Cappadocia — surreal fairy chimneys, ancient underground cities, and iconic hot air balloon rides.",
            "Ephesus — one of the best-preserved ancient Roman cities in the world, near the Aegean coast.",
            "Pamukkale's white calcium terraces and thermal pools, a UNESCO World Heritage Site.",
            "The Grand Bazaar in Istanbul — one of the world's oldest and largest covered markets with 4,000 shops.",
        ],
        "cuisine": [
            "Kebabs — from Adana's spicy minced meat to Iskender's buttery sliced lamb over bread.",
            "Baklava — layers of crispy filo pastry filled with pistachios and soaked in sweet syrup.",
            "Meze platters — a rich spread of hummus, cacık, stuffed vine leaves, and grilled vegetables.",
            "Simit and Börek — sesame-crusted bread rings and flaky pastries, the soul of Turkish street food.",
            "Turkish breakfast — an elaborate spread of cheese, olives, eggs, tomatoes, honey, and fresh bread.",
        ],
    },
    "japan": {
        "tourism": [
            "Mount Fuji — Japan's iconic sacred peak and a UNESCO World Heritage Site near Tokyo.",
            "Kyoto's Fushimi Inari Shrine — thousands of vermillion torii gates winding through forested hills.",
            "Tokyo's Shibuya Crossing, Senso-ji Temple in Asakusa, and the neon-lit streets of Shinjuku.",
            "Hiroshima Peace Memorial and the floating torii gate of Miyajima Island.",
            "The ancient temples and deer parks of Nara, and Osaka's vibrant Dotonbori food street.",
        ],
        "cuisine": [
            "Sushi and Sashimi — fresh raw fish over vinegared rice, a cornerstone of Japanese culinary art.",
            "Ramen — rich broth noodle soup with regional varieties from Sapporo's miso to Hakata's tonkotsu.",
            "Tempura — lightly battered and fried seafood and vegetables, crispy and delicate.",
            "Takoyaki and Okonomiyaki — Osaka's beloved street food; octopus balls and savory pancakes.",
            "Wagyu beef — world-famous marbled Japanese beef, best enjoyed as yakiniku or in a hot pot.",
        ],
    },
    "france": {
        "tourism": [
            "The Eiffel Tower and the Louvre Museum — Paris's most iconic landmarks drawing millions annually.",
            "The Palace of Versailles — a breathtaking royal château with vast gardens outside Paris.",
            "The French Riviera — glamorous coastline with Nice, Cannes, and Monaco.",
            "Mont Saint-Michel — a stunning medieval abbey island off the Normandy coast.",
            "The Loire Valley châteaux — a UNESCO-listed region of Renaissance castles and vineyards.",
        ],
        "cuisine": [
            "Croissants and baguettes — buttery, flaky pastries and crusty bread, a French breakfast staple.",
            "Coq au Vin and Beef Bourguignon — rich, slow-braised meat dishes from the heart of French cooking.",
            "Escargot and Foie Gras — classic French delicacies found in traditional Parisian bistros.",
            "Crêpes and Macarons — sweet thin pancakes and colorful almond meringue sandwich cookies.",
            "French cheese and wine — over 400 cheese varieties and world-class wines from Bordeaux and Burgundy.",
        ],
    },
    "italy": {
        "tourism": [
            "The Colosseum and Roman Forum — ancient Roman amphitheater and ruins in the heart of Rome.",
            "Venice's Grand Canal and gondola rides through a city built entirely on water.",
            "Florence's Uffizi Gallery, Duomo Cathedral, and Michelangelo's David.",
            "The Amalfi Coast — dramatic cliffside villages, turquoise waters, and lemon groves.",
            "Pompeii — the remarkably preserved ancient city buried by Mount Vesuvius in 79 AD.",
        ],
        "cuisine": [
            "Neapolitan pizza — wood-fired, chewy crust with San Marzano tomatoes and fresh mozzarella.",
            "Pasta in all forms — from Rome's Carbonara and Cacio e Pepe to Bologna's Ragù Bolognese.",
            "Gelato — Italian ice cream, richer and denser than regular ice cream, in hundreds of flavors.",
            "Risotto and Osso Buco — creamy Milanese rice dish and braised veal shank from Lombardy.",
            "Tiramisu and Cannoli — iconic Italian desserts loved around the world.",
        ],
    },
    "china": {
        "tourism": [
            "The Great Wall of China — one of the greatest architectural feats in human history.",
            "The Forbidden City in Beijing — a vast imperial palace complex with 9,999 rooms.",
            "The Terracotta Army in Xi'an — thousands of life-size clay soldiers guarding Emperor Qin's tomb.",
            "Zhangjiajie National Forest Park — towering sandstone pillars that inspired the movie Avatar.",
            "Li River cruise in Guilin — stunning karst mountains reflected in calm green waters.",
        ],
        "cuisine": [
            "Peking Duck — crispy roasted duck served with thin pancakes, hoisin sauce, and scallions.",
            "Dim Sum — bite-sized dumplings, buns, and rolls served in bamboo steamers, a Cantonese tradition.",
            "Kung Pao Chicken and Mapo Tofu — bold, spicy Sichuan classics with numbing peppercorns.",
            "Hot Pot — a communal simmering broth at the table where you cook your own meat and vegetables.",
            "Xiaolongbao — delicate soup dumplings filled with pork and rich broth, a Shanghai specialty.",
        ],
    },
    "south korea": {
        "tourism": [
            "Gyeongbokgung Palace in Seoul — a grand Joseon-era royal palace with changing of the guard ceremony.",
            "Jeju Island — a volcanic island with stunning lava tubes, waterfalls, and Hallasan Mountain.",
            "Bukchon Hanok Village — a preserved neighborhood of traditional Korean hanok houses in Seoul.",
            "Seoraksan National Park — dramatic granite peaks and Buddhist temples in autumn foliage.",
            "The DMZ (Demilitarized Zone) — a unique and sobering glimpse into Korean history and division.",
        ],
        "cuisine": [
            "Kimchi — fermented spicy cabbage, the national dish served with every Korean meal.",
            "Korean BBQ — grilling marinated beef bulgogi and pork belly galbi at the table.",
            "Bibimbap — a colorful bowl of rice topped with seasoned vegetables, egg, and gochujang paste.",
            "Tteokbokki and Hotteok — spicy rice cakes and sweet filled pancakes, iconic street foods.",
            "Samgyetang — whole chicken stuffed with ginseng and rice, a nourishing Korean soup.",
        ],
    },
    "germany": {
        "tourism": [
            "Neuschwanstein Castle — a fairy-tale Bavarian castle that inspired Disney's Sleeping Beauty.",
            "Brandenburg Gate and the Berlin Wall Memorial — powerful symbols of Germany's divided history.",
            "The Rhine Valley — medieval castles, vineyard-covered slopes, and charming riverside towns.",
            "Cologne Cathedral — a towering Gothic masterpiece and UNESCO World Heritage Site.",
            "Oktoberfest in Munich — the world's largest beer festival held every September and October.",
        ],
        "cuisine": [
            "Bratwurst and Weisswurst — grilled and boiled sausages, the heart of German street food.",
            "Pretzels and Pumpernickel — soft salted bread knots and dense dark rye bread.",
            "Sauerbraten and Schnitzel — slow-marinated pot roast and breaded fried veal or pork cutlets.",
            "Black Forest Cake — layers of chocolate sponge, whipped cream, and cherries from Baden.",
            "German beer — over 1,300 breweries producing lagers, wheat beers, and dark bocks.",
        ],
    },
    "brazil": {
        "tourism": [
            "Christ the Redeemer and Sugarloaf Mountain — Rio de Janeiro's iconic landmarks overlooking Guanabara Bay.",
            "The Amazon Rainforest — the world's largest tropical rainforest with unmatched biodiversity.",
            "Iguazu Falls — one of the world's largest and most spectacular waterfall systems.",
            "Salvador's Pelourinho — a vibrant UNESCO-listed colonial historic center full of Afro-Brazilian culture.",
            "The Pantanal — the world's largest tropical wetland and one of the best wildlife watching destinations.",
        ],
        "cuisine": [
            "Feijoada — a hearty black bean and pork stew, Brazil's beloved national dish.",
            "Churrasco — Brazilian-style barbecue with skewers of various meats carved tableside.",
            "Pão de Queijo — warm, chewy cheese bread balls, a beloved Brazilian snack.",
            "Açaí bowl — thick, purple açaí berry smoothie topped with granola and fresh fruits.",
            "Coxinha and Pastel — crispy fried chicken croquettes and pastry pockets filled with various fillings.",
        ],
    },
    "egypt": {
        "tourism": [
            "The Pyramids of Giza and the Great Sphinx — the last surviving wonder of the ancient world.",
            "Luxor's Valley of the Kings — ancient royal tombs including Tutankhamun's burial chamber.",
            "The Egyptian Museum in Cairo — home to over 120,000 ancient artifacts including royal mummies.",
            "Abu Simbel — two massive rock temples built by Ramesses II on the banks of Lake Nasser.",
            "The Red Sea Riviera — world-class diving, snorkeling, and beach resorts at Hurghada and Sharm El-Sheikh.",
        ],
        "cuisine": [
            "Koshari — Egypt's national dish of rice, lentils, pasta, and crispy onions with spiced tomato sauce.",
            "Ful Medames — slow-cooked fava beans with olive oil and spices, the classic Egyptian breakfast.",
            "Shawarma and Kofta — spiced meat wraps and grilled minced meat skewers from Cairo's street stalls.",
            "Molokhia — a thick green soup made from jute leaves, served over rice with rabbit or chicken.",
            "Basbousa and Konafa — semolina syrup cake and shredded pastry with cream, classic Egyptian sweets.",
        ],
    },
    "morocco": {
        "tourism": [
            "Marrakech's Djemaa el-Fna square — a UNESCO-listed marketplace alive with storytellers and food stalls.",
            "The blue-painted city of Chefchaouen nestled in the Rif Mountains.",
            "Fes el-Bali — the world's largest car-free urban area and a perfectly preserved medieval medina.",
            "The Sahara Desert at Merzouga — camel treks and overnight camps among towering sand dunes.",
            "Aït Benhaddou — a dramatic fortified mud-brick village and UNESCO World Heritage Site.",
        ],
        "cuisine": [
            "Tagine — slow-cooked stews of lamb, chicken, or vegetables in a conical clay pot with preserved lemon.",
            "Couscous — steamed semolina grains served with seven vegetables and tender braised meat.",
            "Pastilla — a flaky filo pastry pie filled with spiced pigeon or chicken, almonds, and cinnamon.",
            "Harira soup — a thick tomato and lentil soup traditionally used to break the Ramadan fast.",
            "Mint tea and Msemen — sweet fresh mint tea poured from height and flaky pan-fried flatbreads.",
        ],
    },
    "thailand": {
        "tourism": [
            "Bangkok's Grand Palace and Wat Phra Kaew — the stunning royal complex housing the Emerald Buddha.",
            "Chiang Mai's ancient walled city, night markets, and elephant sanctuaries.",
            "The islands of Phuket, Koh Samui, and Koh Phi Phi — crystal-clear waters and white sand beaches.",
            "Ayutthaya Historical Park — the ruins of Thailand's ancient capital, a UNESCO World Heritage Site.",
            "The floating markets of Damnoen Saduak — colorful boats selling fresh produce on the canals.",
        ],
        "cuisine": [
            "Pad Thai — stir-fried rice noodles with shrimp, egg, bean sprouts, and crushed peanuts.",
            "Tom Yum Goong — a hot and sour lemongrass soup with shrimp, galangal, and kaffir lime leaves.",
            "Som Tum — a fiery green papaya salad pounded in a mortar with chili, lime, and fish sauce.",
            "Massaman and Green Curry — rich coconut milk curries with potatoes, peanuts, and fresh herbs.",
            "Mango Sticky Rice — sweet glutinous rice with fresh ripe mango and coconut cream sauce.",
        ],
    },
    "united states": {
        "tourism": [
            "New York City's Times Square, Central Park, Statue of Liberty, and the Brooklyn Bridge.",
            "The Grand Canyon — one of the world's greatest natural wonders carved by the Colorado River.",
            "Yellowstone National Park — the world's first national park with geysers, hot springs, and wildlife.",
            "Las Vegas Strip — a dazzling stretch of luxury hotels, casinos, and world-class entertainment.",
            "Walt Disney World in Orlando — the most visited theme park resort on Earth.",
        ],
        "cuisine": [
            "Burgers and BBQ — from smash burgers to slow-smoked Texas brisket and Carolina pulled pork.",
            "New York-style pizza and Chicago deep-dish — two iconic regional pizza rivalries.",
            "Lobster rolls, clam chowder, and crab cakes — fresh seafood staples from New England and the Chesapeake.",
            "Southern fried chicken, biscuits, and gumbo — comfort food classics from the American South.",
            "Apple pie, chocolate chip cookies, and donuts — beloved American desserts and sweet treats.",
        ],
    },
    "united kingdom": {
        "tourism": [
            "London's Big Ben, Tower of London, Buckingham Palace, and the British Museum.",
            "Stonehenge — a mysterious prehistoric monument on Salisbury Plain, over 5,000 years old.",
            "The Scottish Highlands — dramatic lochs, glens, and castles including the famous Loch Ness.",
            "Bath's Roman Baths and Georgian architecture — a perfectly preserved ancient spa city.",
            "The Cotswolds — picturesque honey-stone villages, rolling hills, and charming country pubs.",
        ],
        "cuisine": [
            "Fish and Chips — battered and fried cod or haddock with thick-cut chips, a British institution.",
            "Full English Breakfast — bacon, eggs, sausages, baked beans, black pudding, and toast.",
            "Chicken Tikka Masala — Britain's most popular dish, a legacy of South Asian immigration.",
            "Afternoon Tea — finger sandwiches, scones with clotted cream and jam, and fine loose-leaf tea.",
            "Sticky Toffee Pudding and Eton Mess — beloved British desserts found in every pub and restaurant.",
        ],
    },
    "spain": {
        "tourism": [
            "Sagrada Família in Barcelona — Gaudí's breathtaking unfinished basilica, a UNESCO World Heritage Site.",
            "The Alhambra Palace in Granada — a stunning Moorish fortress with intricate Islamic architecture.",
            "Madrid's Prado Museum — one of the world's finest art collections with Velázquez and Goya.",
            "San Sebastián's Old Town and La Concha beach — one of Europe's most beautiful coastal cities.",
            "The Camino de Santiago — a famous pilgrimage route through northern Spain ending at the cathedral.",
        ],
        "cuisine": [
            "Paella — saffron-infused rice with seafood or chicken, the iconic dish of Valencia.",
            "Tapas — small plates of jamón ibérico, patatas bravas, gambas al ajillo, and tortilla española.",
            "Gazpacho and Salmorejo — chilled tomato soups from Andalusia, perfect for hot summers.",
            "Churros with chocolate — crispy fried dough dipped in thick hot chocolate, a classic Spanish snack.",
            "Jamón Ibérico — world-famous dry-cured Iberian ham aged for years, sliced paper-thin.",
        ],
    },
    "greece": {
        "tourism": [
            "The Acropolis and Parthenon in Athens — the pinnacle of ancient Greek civilization.",
            "Santorini's blue-domed churches and whitewashed villages perched above volcanic cliffs.",
            "Mykonos — a glamorous island famous for windmills, beaches, and vibrant nightlife.",
            "Delphi — the sacred sanctuary of Apollo and the Oracle, set dramatically on Mount Parnassus.",
            "Meteora — ancient monasteries perched atop towering rock pillars in central Greece.",
        ],
        "cuisine": [
            "Moussaka — layers of eggplant, spiced minced meat, and béchamel sauce, baked until golden.",
            "Souvlaki and Gyros — grilled meat skewers and wraps with tzatziki, tomato, and onion.",
            "Spanakopita — flaky filo pastry filled with spinach, feta cheese, and fresh herbs.",
            "Fresh seafood — grilled octopus, calamari, and sea bream caught daily on the Aegean islands.",
            "Baklava and Loukoumades — honey-soaked nut pastries and crispy fried dough balls with syrup.",
        ],
    },
    "russia": {
        "tourism": [
            "Red Square and the Kremlin in Moscow — the historic heart of Russia with Saint Basil's Cathedral.",
            "The Hermitage Museum in St. Petersburg — one of the world's largest art museums in a lavish palace.",
            "Lake Baikal — the world's deepest and oldest freshwater lake in Siberia.",
            "The Trans-Siberian Railway — the world's longest railway journey spanning 9,289 km across Russia.",
            "Peterhof Palace — the 'Russian Versailles' with spectacular fountains and golden statues.",
        ],
        "cuisine": [
            "Borscht — a vibrant beet soup served hot or cold with a dollop of sour cream.",
            "Beef Stroganoff — tender strips of beef in a rich creamy mushroom sauce over noodles.",
            "Pelmeni — Russian dumplings filled with minced meat and served with butter or sour cream.",
            "Blini — thin Russian pancakes served with caviar, smoked salmon, or sweet jam.",
            "Olivier salad and Shashlik — the classic Russian potato salad and marinated grilled meat skewers.",
        ],
    },
    "saudi arabia": {
        "tourism": [
            "Mecca and Medina — the two holiest cities in Islam, visited by millions of pilgrims annually.",
            "AlUla and Hegra — a breathtaking ancient Nabataean city carved into rose-red rock formations.",
            "Diriyah — the UNESCO-listed birthplace of the Saudi state, now a stunning cultural district.",
            "The Edge of the World (Jebel Fihrayn) — dramatic cliff escarpments with panoramic desert views.",
            "Al-Ahsa Oasis — the world's largest natural oasis, a UNESCO World Heritage Site.",
        ],
        "cuisine": [
            "Kabsa — fragrant basmati rice slow-cooked with lamb or chicken and a blend of warming spices.",
            "Mandi — tender slow-roasted meat and rice cooked in a tandoor underground pit.",
            "Jareesh — crushed wheat cooked with meat and spices, a traditional Saudi comfort food.",
            "Mutabbaq — a stuffed pan-fried pastry filled with spiced minced meat and egg.",
            "Dates and Arabic coffee — Medjool dates and cardamom-spiced qahwa, the symbol of Saudi hospitality.",
        ],
    },
    "iran": {
        "tourism": [
            "Persepolis — the magnificent ruins of the ancient Persian Empire's ceremonial capital near Shiraz.",
            "Isfahan's Naqsh-e Jahan Square — a UNESCO-listed plaza surrounded by stunning Safavid architecture.",
            "The ancient desert city of Yazd — a UNESCO World Heritage Site with wind towers and Zoroastrian temples.",
            "Shiraz's Nasir al-Mulk Mosque — the dazzling Pink Mosque with kaleidoscopic stained glass.",
            "Tehran's Golestan Palace — a lavish Qajar-era royal complex in the heart of the capital.",
        ],
        "cuisine": [
            "Ghormeh Sabzi — a fragrant herb, kidney bean, and lamb stew, considered Iran's national dish.",
            "Chelo Kebab — saffron-marinated grilled meat over buttered rice, served with grilled tomatoes.",
            "Fesenjan — a rich pomegranate and walnut stew with duck or chicken, deeply aromatic.",
            "Ash Reshteh — a thick noodle and herb soup topped with kashk (whey) and fried onions.",
            "Baklava and Sohan — Persian saffron-pistachio pastries and brittle toffee, famous in Qom and Yazd.",
        ],
    },
}


def _fetch_wiki_live(country_name: str) -> dict:
    """
    Live Wikipedia fallback for countries not in the hardcoded list.
    Uses search snippets to extract relevant tourism and cuisine info.
    """
    import re

    def search_snippets(query):
        result = safe_get(WIKI_API, params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 5,
        })
        if not result or not result.get("ok"):
            return []
        hits = result.get("data", {}).get("query", {}).get("search", [])
        snippets = []
        for hit in hits:
            clean = re.sub(r'<[^>]*>', '', hit.get("snippet", "")).strip()
            if len(clean) > 40:
                snippets.append(clean[0].upper() + clean[1:] + ("..." if not clean.endswith(".") else ""))
        return snippets[:3]

    country = country_name.strip().title()
    tourism = search_snippets(f'"{country}" famous landmarks tourist attractions historical sites')
    cuisine = search_snippets(f'"{country}" traditional food cuisine popular dishes')

    return {
        "tourism": tourism or [f"Explore the rich cultural heritage, historic landmarks, and natural wonders of {country}."],
        "cuisine": cuisine or [f"Discover the unique traditional flavors, spices, and culinary traditions of {country}."],
    }


def get_wiki_info(country_name: str) -> dict:
    """
    Returns tourism and cuisine info for any country.
    Uses hardcoded high-quality data for major destinations,
    falls back to live Wikipedia search for others.
    """
    key = country_name.strip().lower()

    if key in COUNTRY_TRAVEL_DATA:
        return COUNTRY_TRAVEL_DATA[key]

    return _fetch_wiki_live(country_name)