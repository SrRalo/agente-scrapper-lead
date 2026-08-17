import re
import json
import urllib.parse
import serpapi
from backend.config import SERPAPI_KEY


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:80].strip("-")


async def scrape_google_maps(
    query: str,
    location: str = "",
    max_results: int = 20,
    min_rating: float = 0,
) -> dict:
    if not SERPAPI_KEY:
        return {"error": "SERPAPI_KEY no configurada en .env"}

    params = {
        "engine": "google_maps",
        "type": "search",
        "q": query,
        "api_key": SERPAPI_KEY,
        "hl": "es",
    }

    if location:
        coords = _resolve_location(location)
        if coords:
            params["ll"] = f"@{coords['lat']},{coords['lon']},14z"
        else:
            params["location"] = location
            params["z"] = "14"

    if min_rating > 0:
        params["min_rating"] = str(min_rating)

    all_leads = []
    pages_needed = (max_results + 19) // 20
    seen_slugs = set()

    try:
        client = serpapi.Client(api_key=SERPAPI_KEY)

        for page in range(pages_needed):
            if page > 0:
                params["start"] = page * 20

            search = client.search(params)
            results = search.get("local_results", [])

            if not results:
                break

            for r in results:
                business_name = r.get("title", "")
                if not business_name:
                    continue

                slug = slugify(business_name)
                if slug in seen_slugs:
                    continue
                seen_slugs.add(slug)

                place_id = r.get("place_id", "")
                search_name = urllib.parse.quote(f"{business_name} {location}" if location else business_name)
                google_url = f"https://www.google.com/maps/search/{search_name}"

                lead = {
                    "business_name": business_name,
                    "business_type": r.get("type", ""),
                    "category": r.get("category", ""),
                    "description_short": r.get("description", ""),
                    "phone": r.get("phone", ""),
                    "website": r.get("website", ""),
                    "address": r.get("address", ""),
                    "city": r.get("city", "") or (location.split(",")[0].strip() if location else ""),
                    "country": r.get("country", ""),
                    "rating": r.get("rating", 0),
                    "reviews_count": r.get("reviews", 0),
                    "place_id": place_id,
                    "google_url": google_url,
                    "logo_url": r.get("thumbnail", ""),
                    "hero_url": "",
                    "images": json.dumps(r.get("images", [])),
                    "email": "",
                    "slug": slug,
                }
                all_leads.append(lead)

                if len(all_leads) >= max_results:
                    break

            if len(all_leads) >= max_results:
                break

        return {
            "status": "ok",
            "query": query,
            "location": location,
            "count": len(all_leads),
            "leads": all_leads[:max_results],
        }

    except Exception as e:
        return {"error": str(e), "status": "error"}


LOCATION_COORDS = {
    "buenos aires": {"lat": -34.6037, "lon": -58.3816},
    "mendoza": {"lat": -32.8895, "lon": -68.8458},
    "cordoba": {"lat": -31.4201, "lon": -64.1888},
    "rosario": {"lat": -32.9468, "lon": -60.6393},
    "madrid": {"lat": 40.4168, "lon": -3.7038},
    "barcelona": {"lat": 41.3874, "lon": 2.1686},
    "mexico city": {"lat": 19.4326, "lon": -99.1332},
    "ciudad de mexico": {"lat": 19.4326, "lon": -99.1332},
    "guadalajara": {"lat": 20.6597, "lon": -103.3496},
    "monterrey": {"lat": 25.6866, "lon": -100.3161},
    "bogota": {"lat": 4.711, "lon": -74.0721},
    "lima": {"lat": -12.0464, "lon": -77.0428},
    "santiago": {"lat": -33.4489, "lon": -70.6693},
    "medellin": {"lat": 6.2476, "lon": -75.5658},
    "cali": {"lat": 3.4516, "lon": -76.532},
    "new york": {"lat": 40.7128, "lon": -74.006},
    "miami": {"lat": 25.7617, "lon": -80.1918},
    "los angeles": {"lat": 34.0522, "lon": -118.2437},
    "chicago": {"lat": 41.8781, "lon": -87.6298},
    "houston": {"lat": 29.7604, "lon": -95.3698},
    "sao paulo": {"lat": -23.5505, "lon": -46.6333},
    "rio de janeiro": {"lat": -22.9068, "lon": -43.1729},
    "buenos aires, argentina": {"lat": -34.6037, "lon": -58.3816},
    "madrid, espana": {"lat": 40.4168, "lon": -3.7038},
    "mexico, mexico": {"lat": 19.4326, "lon": -99.1332},
}


def _resolve_location(location: str) -> dict:
    loc_lower = location.lower().strip()
    if loc_lower in LOCATION_COORDS:
        return LOCATION_COORDS[loc_lower]
    return None


def _extract_city(address: str, fallback_location: str = "") -> str:
    if not address:
        return fallback_location.split(",")[0].strip() if fallback_location else ""

    parts = [p.strip() for p in address.split(",")]

    for part in parts:
        clean = part.strip()
        if not clean:
            continue
        if "Buenos Aires" in clean or "Ciudad Aut" in clean or "Cdad" in clean:
            return "Buenos Aires"
        if any(skip in clean.lower() for skip in ["argentina", "mexico", "espana", "spain", "usa", "united states"]):
            continue
        if clean.startswith("C") and len(clean) > 1 and clean[1].isdigit():
            continue
        if clean.startswith(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")):
            continue
        if len(clean) <= 5:
            continue
        return clean

    if fallback_location:
        return fallback_location.split(",")[0].strip()
    return ""


async def scrape_place_details(place_id: str) -> dict:
    if not SERPAPI_KEY:
        return {"error": "SERPAPI_KEY no configurada"}

    params = {
        "engine": "google_maps",
        "place_id": place_id,
        "api_key": SERPAPI_KEY,
        "hl": "es",
    }

    try:
        client = serpapi.Client(api_key=SERPAPI_KEY)
        search = client.search(params)
        result = search.get("place_results", {})

        return {
            "status": "ok",
            "data": {
                "title": result.get("title", ""),
                "type": result.get("type", ""),
                "description": result.get("description", ""),
                "phone": result.get("phone", ""),
                "website": result.get("website", ""),
                "address": result.get("address", ""),
                "rating": result.get("rating", 0),
                "reviews": result.get("reviews", 0),
                "hours": result.get("hours", ""),
                "service_options": result.get("service_options", {}),
                "menu": result.get("menu", ""),
                "price": result.get("price", ""),
                "type_of_place": result.get("type_of_place", ""),
                "images": [img.get("image", "") for img in result.get("images", [])],
            },
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}
