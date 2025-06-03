from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import config
import logging

# Configurar el logger
logger = logging.getLogger(__name__)


def validate_database_url(url: str):
    """
    Válida que la URL de la base de datos tenga un formato correcto.
    """
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ("mysql+aiomysql", "mssql+aioodbc"):
        raise ValueError("Esquema de URL de base de datos no soportado.")
    if not parsed_url.hostname or not parsed_url.path:
        raise ValueError("URL de base de datos incompleta o inválida.")


def create_engine_from_config():
    """
    Crea un motor asíncrono de SQLAlchemy basado en la URL de la base de datos
    proporcionada en la configuración.

    Returns:
        AsyncEngine: Un motor asíncrono de SQLAlchemy configurado.

    Raises:
        ValueError: Si la URL de la base de datos no es válida o no es compatible.
    """
    DATABASE_URL = str(config.DATABASE_URL)
    validate_database_url(DATABASE_URL)

    if DATABASE_URL.startswith("mysql"):
        compatible_engine = create_async_engine(
            DATABASE_URL, pool_pre_ping=True, echo=True
        )
    elif DATABASE_URL.startswith("mssql"):
        compatible_engine = create_async_engine(
            DATABASE_URL, pool_pre_ping=True, echo=True
        )
    else:
        raise ValueError("La URL de la base de datos no es válida o no es compatible.")

    return compatible_engine


# Crear el motor de base de datos asíncrono
engine = create_engine_from_config()


# Crear una fábrica de sesiones asíncronas
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# Función para obtener una sesión de base de datos asíncrona
async def get_db() -> AsyncSession:
    """
    Generador que proporciona una sesión de base de datos asíncrona.

    Yields:
        AsyncSession: Una sesión de base de datos asíncrona.

    Raises:
        SQLAlchemyError: Si ocurre un error durante el uso de la sesión.
    """
    async with async_session() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            logger.error(f"Error en la sesión de la base de datos: {e}")
            raise


def create_sync_engine_from_config():
    """
    Crea un motor síncrono de SQLAlchemy basado en la URL de la base de datos
    proporcionada en la configuración.

    Returns:
        Engine: Un motor síncrono de SQLAlchemy configurado.

    Raises:
        ValueError: Si la URL de la base de datos no es válida o no es compatible.
    """
    sync_db_url = str(config.DATABASE_URL)

    # Cambiar el esquema de la URL para que sea síncrono
    if sync_db_url.startswith("mysql+aiomysql"):
        sync_db_url = sync_db_url.replace("mysql+aiomysql", "mysql+pymysql", 1)
        logger.info("Usando URL síncrona para MySQL")
    elif sync_db_url.startswith("mssql+aioodbc"):
        sync_db_url = sync_db_url.replace("mssql+aioodbc", "mssql+pyodbc", 1)
        logger.info("Usando URL síncrona para SQL Server")
    else:
        raise ValueError("La URL de la base de datos no es válida o no es compatible.")

    return create_engine(sync_db_url, pool_pre_ping=True, echo=True)


# Crear el motor síncrono
try:
    sync_engine = create_sync_engine_from_config()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
    logger.info(f"Motor síncrono y SessionLocal creados para: {sync_engine.url}")
except Exception as e:
    logger.error(f"Error al crear el motor síncrono o SessionLocal: {e}")


def get_sync_db():
    """
    Función que proporciona una sesión de base de datos síncrona.
    Útil para scripts como seed_data.py que no requieren async.

    Returns:
        Session: Una sesión de base de datos síncrona.
    """
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
