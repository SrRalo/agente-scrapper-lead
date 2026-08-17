from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from backend.database import fetch_one, fetch_all, execute, execute_returning
from backend.auth import get_current_user
from backend.schemas import LeadUpdate

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.get("")
async def list_leads(
    status: Optional[str] = None,
    search: Optional[str] = None,
    user: dict = Depends(get_current_user),
):
    query = "SELECT * FROM leads WHERE 1=1"
    params = []
    idx = 1

    if status:
        query += f" AND status = ${idx}"
        params.append(status)
        idx += 1

    if search:
        query += f" AND (business_name ILIKE ${idx} OR category ILIKE ${idx} OR city ILIKE ${idx})"
        params.append(f"%{search}%")
        idx += 1

    query += " ORDER BY created_at DESC"
    return await fetch_all(query, *params)


@router.get("/stats/summary")
async def get_stats(user: dict = Depends(get_current_user)):
    rows = await fetch_all(
        "SELECT status, COUNT(*) as count FROM leads GROUP BY status"
    )
    stats = {row["status"]: row["count"] for row in rows}

    total_row = await fetch_one("SELECT COUNT(*) as total FROM leads")
    total = total_row["total"] if total_row else 0

    return {"total": total, "by_status": stats}


@router.get("/{lead_id}")
async def get_lead(lead_id: int, user: dict = Depends(get_current_user)):
    row = await fetch_one("SELECT * FROM leads WHERE id = $1", lead_id)
    if not row:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return row


@router.put("/{lead_id}")
async def update_lead(
    lead_id: int, update: LeadUpdate, user: dict = Depends(get_current_user)
):
    existing = await fetch_one("SELECT id FROM leads WHERE id = $1", lead_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    updates = []
    params = []
    idx = 1

    for field, value in update.model_dump(exclude_unset=True).items():
        updates.append(f"{field} = ${idx}")
        params.append(value)
        idx += 1

    if not updates:
        raise HTTPException(status_code=400, detail="Sin cambios")

    updates.append(f"updated_at = ${idx}")
    params.append(datetime.now().isoformat())
    idx += 1

    params.append(lead_id)
    await execute(
        f"UPDATE leads SET {', '.join(updates)} WHERE id = ${idx}", *params
    )

    return await fetch_one("SELECT * FROM leads WHERE id = $1", lead_id)


@router.delete("/{lead_id}")
async def delete_lead(lead_id: int, user: dict = Depends(get_current_user)):
    existing = await fetch_one("SELECT id FROM leads WHERE id = $1", lead_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    await execute("DELETE FROM leads WHERE id = $1", lead_id)
    return {"detail": "Lead eliminado"}
