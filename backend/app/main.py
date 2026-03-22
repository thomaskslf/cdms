import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.database import Base, engine
from app.routers import auth, customers, projects, documents, versions, comparison, dashboard

STATIC_DIR = Path(__file__).parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    Path("./storage").mkdir(exist_ok=True)
    yield


app = FastAPI(
    title="CDMS – Kundendokumenten-Verwaltung",
    version="1.0.0",
    lifespan=lifespan,
    # Hide docs in production (set HIDE_DOCS=1 env var)
    docs_url=None if os.getenv("HIDE_DOCS") else "/docs",
    redoc_url=None if os.getenv("HIDE_DOCS") else "/redoc",
)

# CORS: allow all origins in demo/production (frontend is served from same origin anyway)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,       prefix="/api/auth")
app.include_router(customers.router,  prefix="/api")
app.include_router(projects.router,   prefix="/api")
app.include_router(documents.router,  prefix="/api")
app.include_router(versions.router,   prefix="/api")
app.include_router(comparison.router, prefix="/api")
app.include_router(dashboard.router,  prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Serve React frontend (static build) — only if built files exist
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str, request: Request):
        """Catch-all: serve index.html for all non-API routes (React Router)."""
        index = STATIC_DIR / "index.html"
        if index.exists():
            return FileResponse(str(index))
        return {"detail": "Frontend not built. Run build.sh first."}, 404
