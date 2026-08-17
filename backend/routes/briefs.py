import json
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from backend.database import fetch_one, execute
from backend.auth import get_current_user
from backend.brief_generator import generate_brief
from backend.schemas import BriefDataUpdate

router = APIRouter(prefix="/api/briefs", tags=["briefs"])


@router.post("/{lead_id}/generate")
async def generate_brief_from_lead(
    lead_id: int, user: dict = Depends(get_current_user)
):
    lead = await fetch_one("SELECT * FROM leads WHERE id = $1", lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    try:
        content = generate_brief(lead)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando brief: {str(e)}")

    await execute(
        "UPDATE leads SET status = 'brief_generated', brief_content = $1, updated_at = $2 WHERE id = $3",
        content, datetime.now().isoformat(), lead_id,
    )

    return {
        "status": "ok",
        "slug": lead["slug"],
        "message": f"Brief generado para {lead['business_name']}",
    }


@router.get("/{lead_id}/raw")
async def get_brief_raw(lead_id: int, user: dict = Depends(get_current_user)):
    lead = await fetch_one("SELECT slug, brief_content FROM leads WHERE id = $1", lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    if lead.get("brief_content"):
        return PlainTextResponse(lead["brief_content"], media_type="text/markdown")

    slug = lead["slug"]
    from backend.config import BRIEFS_DIR
    filepath = BRIEFS_DIR / f"{slug}.md"
    if filepath.exists():
        content = filepath.read_text(encoding="utf-8")
        await execute(
            "UPDATE leads SET brief_content = $1 WHERE id = $2",
            content, lead_id,
        )
        return PlainTextResponse(content, media_type="text/markdown")

    raise HTTPException(status_code=404, detail="Brief no generado aún")


@router.get("/{lead_id}/download")
async def download_brief(lead_id: int, user: dict = Depends(get_current_user)):
    lead = await fetch_one("SELECT slug, brief_content, business_name FROM leads WHERE id = $1", lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    content = lead.get("brief_content", "")
    if not content:
        from backend.config import BRIEFS_DIR
        filepath = BRIEFS_DIR / f"{lead['slug']}.md"
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")

    if not content:
        raise HTTPException(status_code=404, detail="Brief no generado aún")

    from fastapi.responses import Response
    filename = f"brief-{lead['slug']}.md"
    return Response(
        content=content,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


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
