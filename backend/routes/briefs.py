import json
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from backend.database import fetch_one, execute
from backend.auth import get_current_user
from backend.brief_generator import generate_brief
from backend.schemas import BriefDataUpdate
from backend.config import BRIEFS_DIR

router = APIRouter(prefix="/api/briefs", tags=["briefs"])


@router.post("/{lead_id}/generate")
async def generate_brief_from_lead(
    lead_id: int, user: dict = Depends(get_current_user)
):
    lead = await fetch_one("SELECT * FROM leads WHERE id = $1", lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    try:
        filepath = generate_brief(lead)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando brief: {str(e)}")

    await execute(
        "UPDATE leads SET status = 'brief_generated', updated_at = $1 WHERE id = $2",
        datetime.now().isoformat(), lead_id,
    )

    return {
        "status": "ok",
        "filepath": filepath,
        "slug": lead["slug"],
        "message": f"Brief generado: {filepath}",
    }


@router.get("/{lead_id}/raw")
async def get_brief_raw(lead_id: int, user: dict = Depends(get_current_user)):
    lead = await fetch_one("SELECT slug FROM leads WHERE id = $1", lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    slug = lead["slug"]
    filepath = BRIEFS_DIR / f"{slug}.md"
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Brief no generado aún")

    content = filepath.read_text(encoding="utf-8")
    return PlainTextResponse(content, media_type="text/markdown")


@router.put("/{lead_id}/brief-data")
async def update_brief_data(
    lead_id: int,
    data: BriefDataUpdate,
    user: dict = Depends(get_current_user),
):
    lead = await fetch_one("SELECT brief_data FROM leads WHERE id = $1", lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    existing = {}
    if lead["brief_data"]:
        try:
            existing = json.loads(lead["brief_data"])
        except json.JSONDecodeError:
            pass

    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            existing[field] = value

    await execute(
        "UPDATE leads SET brief_data = $1, updated_at = $2 WHERE id = $3",
        json.dumps(existing, ensure_ascii=False),
        datetime.now().isoformat(),
        lead_id,
    )

    return {"status": "ok", "brief_data": existing}


@router.get("/{lead_id}/brief-data")
async def get_brief_data(lead_id: int, user: dict = Depends(get_current_user)):
    lead = await fetch_one("SELECT brief_data FROM leads WHERE id = $1", lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    data = {}
    if lead["brief_data"]:
        try:
            data = json.loads(lead["brief_data"])
        except json.JSONDecodeError:
            pass

    return data
