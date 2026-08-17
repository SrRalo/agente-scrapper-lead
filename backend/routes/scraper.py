from fastapi import APIRouter, Depends, HTTPException

from backend.database import fetch_one, execute
from backend.auth import get_current_user
from backend.scraper import scrape_google_maps, scrape_place_details
from backend.schemas import ScrapeRequest

router = APIRouter(prefix="/api/scraper", tags=["scraper"])


@router.post("/search")
async def search_businesses(
    request: ScrapeRequest, user: dict = Depends(get_current_user)
):
    if not request.query.strip():
        return {"status": "error", "error": "Escribe una búsqueda (ej: 'dentistas en Madrid')"}

    result = await scrape_google_maps(
        query=request.query,
        location=request.location,
        max_results=request.max_results,
    )

    if result.get("status") != "ok":
        error_msg = result.get("error", "Error desconocido")
        if "SERPAPI_KEY" in error_msg or "api_key" in error_msg.lower():
            error_msg = "Falta configurar SERPAPI_KEY en el archivo .env. Obtén tu API key en https://serpapi.com"
        return {"status": "error", "error": error_msg}

    inserted = 0
    skipped = 0

    for lead_data in result["leads"]:
        slug = lead_data["slug"]

        existing = await fetch_one(
            "SELECT id FROM leads WHERE slug = $1 OR (business_name = $2 AND city = $3)",
            slug, lead_data["business_name"], lead_data.get("city", ""),
        )
        if existing:
            skipped += 1
            continue

        await execute(
            """INSERT INTO leads 
            (slug, business_name, business_type, category, description_short,
             phone, email, website, address, city, country,
             rating, reviews_count, place_id, google_url,
             logo_url, hero_url, images)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)""",
            slug,
            lead_data["business_name"],
            lead_data["business_type"],
            lead_data["category"],
            lead_data["description_short"],
            lead_data["phone"],
            lead_data["email"],
            lead_data["website"],
            lead_data["address"],
            lead_data["city"],
            lead_data["country"],
            lead_data["rating"],
            lead_data["reviews_count"],
            lead_data["place_id"],
            lead_data["google_url"],
            lead_data["logo_url"],
            lead_data["hero_url"],
            lead_data["images"],
        )
        inserted += 1

    return {
        "status": "ok",
        "query": request.query,
        "location": request.location,
        "total_found": result["count"],
        "inserted": inserted,
        "skipped": skipped,
    }


@router.get("/place/{place_id}")
async def get_place_details(place_id: str, user: dict = Depends(get_current_user)):
    result = await scrape_place_details(place_id)
    if result.get("status") != "ok":
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result
