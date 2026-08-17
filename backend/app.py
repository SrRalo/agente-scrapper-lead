from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pathlib import Path

from backend.database import close_pool
from backend.routes import leads, scraper, briefs


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_pool()


app = FastAPI(
    title="Lead Pipeline - Scraper de Negocios",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leads.router)
app.include_router(scraper.router)
app.include_router(briefs.router)

BASE_DIR = Path(__file__).parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

FAVICON_SVG = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="45" fill="%233b82f6"/><text x="50" y="65" font-size="50" text-anchor="middle" fill="white" font-family="Arial">L</text></svg>'


@app.get("/favicon.ico")
async def favicon():
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")


@app.get("/js/alpine.min.js")
async def serve_alpine():
    return FileResponse(FRONTEND_DIR / "js" / "alpine.min.js", media_type="application/javascript")


@app.get("/login")
async def serve_login():
    return FileResponse(FRONTEND_DIR / "login.html")


@app.get("/")
async def serve_dashboard():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/dashboard")
async def serve_dashboard_alt():
    return FileResponse(FRONTEND_DIR / "index.html")
