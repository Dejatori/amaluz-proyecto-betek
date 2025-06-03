"""
Módulo de configuración para la aplicación Gestión de Comercio Online de Velas.
Este módulo define la configuración específica del entorno y las clases de configuración.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """
    Clase de configuración base para la aplicación.
    Utiliza BaseSettings de Pydantic para cargar variables de entorno.
    """
    ENV_STATE: Optional[str] = None
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )


class GlobalConfig(BaseConfig):
    """
    Configuración global para todos los entornos.
    Contiene parámetros de configuración comunes utilizados en toda la aplicación.
    """
    PROJECT_NAME: Optional[str] = "App"
    API_V1_STR: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    JWT_SECRET: Optional[str] = None
    JWT_EXPIRES_IN: Optional[int] = None
    MAILGUN_API_KEY: Optional[str] = None
    MAILGUN_DOMAIN: Optional[str] = None
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    BACKEND_CORS_ORIGINS: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OLLAMA_API_URL: Optional[str] = None
    DATABASE_URL_PREDICCIONES: Optional[str] = None
    AMALUZ_DATABASE_URL: Optional[str] = None


class DevConfig(GlobalConfig):
    """
    Clase de configuración para el entorno de desarrollo.
    """
    model_config = SettingsConfigDict(env_prefix="DEV_")


class ProdConfig(GlobalConfig):
    """
    Clase de configuración para el entorno de producción.
    """
    model_config = SettingsConfigDict(env_prefix="PROD_")


class TestConfig(GlobalConfig):
    """
    Clase de configuración para el entorno de pruebas.
    """
    # DATABASE_URL: str = "mysql+aiomysql://test_user:test_password@mysql_test:3306/test_db"
    # DATABASE_URL: str = "mssql+aioodbc://sa:StrongPass123!@sqlserver_test:1433/test_db?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    DB_FORCE_ROLL_BACK: bool = True
    PROJECT_NAME:str = "Amaluz (Testing)"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "bfd69137a5e825bf9a0df830e6812b6224924ca087bf7b4e1c38c829369e6c4e"
    JWT_SECRET: str = "2826370bf9eb28e4bc3f5b9f77f80e25f33bebdb8e5834bd34760a7ed4ca1ec5"
    JWT_EXPIRES_IN: int = 11520
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    model_config = SettingsConfigDict(env_prefix="TEST_")


@lru_cache()
def get_config(env_state: str):
    """
    Función para obtener la clase de configuración apropiada según el estado del entorno.
    """
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()


config = get_config(BaseConfig().ENV_STATE)
