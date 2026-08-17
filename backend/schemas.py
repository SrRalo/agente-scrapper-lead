from pydantic import BaseModel
from typing import Optional


class LeadUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    contact_method: Optional[str] = None
    contact_date: Optional[str] = None
    description_short: Optional[str] = None
    business_type: Optional[str] = None
    brief_data: Optional[str] = None
    problem: Optional[str] = None
    problem_key: Optional[str] = None


class ScrapeRequest(BaseModel):
    query: str = ""
    location: str = ""
    max_results: int = 20


class BriefDataUpdate(BaseModel):
    tagline: Optional[str] = None
    tone: Optional[str] = None
    audience: Optional[str] = None
    objective: Optional[str] = None
    hero_title: Optional[str] = None
    hero_subtitle: Optional[str] = None
    cta_text: Optional[str] = None
    cta_url: Optional[str] = None
    features: Optional[list] = None
    faq: Optional[list] = None
    pricing: Optional[list] = None
    testimonials: Optional[list] = None
    colors: Optional[dict] = None
    form_fields: Optional[list] = None
