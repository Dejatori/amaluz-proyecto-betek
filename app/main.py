"""
Módulo principal de la aplicación Gestión de Comercio Online de Velas.
Este módulo configura e inicializa la aplicación FastAPI con sus rutas y middleware.
"""
import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

from app.core.config import config
from app.db.base import Base
from app.db.database import engine
from app.core.logging import configure_logging
# from app.api.endpoints.api_router import api_router - Futura implementación de rutas con FastAPI

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """
    Maneja los eventos de inicio y cierre de la aplicación FastAPI.
    Conecta y desconecta la base de datos.
    """
    configure_logging()
    logger.info("Iniciando la aplicación FastAPI")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Base de datos conectada")
    yield


app = FastAPI(
    title=config.PROJECT_NAME,
    description="Backend API para la gestión de ecommerce",
    version="0.1.0",
    openapi_url=f"{config.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(CorrelationIdMiddleware)

if config.BACKEND_CORS_ORIGINS:
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in config.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Gestión de Comercio Online de Velas"}


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    logger.error("HTTP Exception: %s, %s", exc.status_code, exc.detail)
    return await http_exception_handler(request, exc)
