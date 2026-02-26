"""FastAPI application entry point."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.middleware import RequestIdMiddleware
from app.routes.health import router as health_router
from app.routes.search import router as search_router
from app.routes.profile import router as profile_router
from app.store import get_store

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(
    title="Affirm Agentic Discovery API",
    version="0.1.0",
    description="Agentic search pipeline for financial product discovery",
)

# CORS — allow Expo dev server and web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIdMiddleware)

# Routes
app.include_router(health_router)
app.include_router(search_router)
app.include_router(profile_router)

# Serve Expo web build as static files (if present)
if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")
    app.mount("/_expo", StaticFiles(directory=str(STATIC_DIR / "_expo")), name="expo")

    @app.get("/favicon.ico")
    async def favicon():
        return FileResponse(str(STATIC_DIR / "favicon.ico"))

    @app.get("/{path:path}")
    async def spa_fallback(request: Request, path: str):
        """Serve index.html for any non-API, non-asset route (SPA client-side routing)."""
        file_path = STATIC_DIR / path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(STATIC_DIR / "index.html"))


@app.on_event("startup")
async def startup():
    """Seed in-memory store on startup."""
    store = get_store()
    logging.info(f"Store initialized with {len(store.offers)} offers")
