from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from backend.database import fetch_one, fetch_all, execute, execute_returning
from backend.auth import get_current_user
from backend.schemas import LeadUpdate

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.get("")
async def list_leads(
    status: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    user: dict = Depends(get_current_user),
):
    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)

    where_clauses = ["1=1"]
    params: list = []
    idx = 1

    if status:
        where_clauses.append(f"status = ${idx}")
        params.append(status)
        idx += 1

    if search:
        where_clauses.append(f"(business_name ILIKE ${idx} OR category ILIKE ${idx} OR city ILIKE ${idx})")
        params.append(f"%{search}%")
        idx += 1

    if date_from:
        where_clauses.append(f"created_at >= ${idx}")
        params.append(date_from)
        idx += 1

    if date_to:
        where_clauses.append(f"created_at <= ${idx}")
        params.append(date_to)
        idx += 1

    where_sql = " AND ".join(where_clauses)

    total_row = await fetch_one(f"SELECT COUNT(*) as total FROM leads WHERE {where_sql}", *params)
    total = total_row["total"] if total_row else 0

    offset = (page - 1) * page_size
    rows = await fetch_all(
        f"SELECT * FROM leads WHERE {where_sql} ORDER BY created_at DESC LIMIT {page_size} OFFSET {offset}",
        *params,
    )

    return {"total": total, "page": page, "page_size": page_size, "leads": rows}


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
