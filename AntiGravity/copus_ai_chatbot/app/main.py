"""FastAPI Application Entrypoint."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.sqlite_db import init_sqlite_db
from app.api.whatsapp import router as whatsapp_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("APEX_AI_MAIN")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan manager."""
    logger.info("Initializing APEX AI Dental Assistant Service...")
    init_sqlite_db()
    logger.info("SQLite Relational Knowledge Base initialized.")
    yield
    logger.info("Shutting down APEX AI Service.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-Grade Zero-Hallucination WhatsApp Clinical Assistant for Apex Dental Center",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(whatsapp_router)


@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
async def health_check():
    """System health and readiness check endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "online",
            "project": settings.PROJECT_NAME,
            "environment": settings.ENVIRONMENT,
            "architecture": "AI Sandwich (Ingress -> LLM Extraction -> DB Lookup -> LLM Synthesis -> Egress)"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
