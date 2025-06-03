"""
Módulo de configuración de logging para la API de la tienda.
Este módulo configura los registradores, controladores, formateadores y filtros
para un registro completo de la aplicación, incluyendo salidas a consola, archivos
y servicios externos.
"""
# https://docs.python.org/3/howto/logging.html#logging-flow
import logging
from logging.config import dictConfig
from pathlib import Path

from email_validator import EmailNotValidError, validate_email

from app.core.config import DevConfig, config


def obfuscated(email: str, obfuscated_length: int) -> str:
    """
    Ofusca la dirección de correo electrónico para fines de registro.

    Utiliza email-validator para verificar que el correo sea válido
    antes de procesarlo, manteniendo el dominio visible, pero ocultando
    parte del nombre de usuario.
    """
    if not email:
        return email

    try:
        # Validar que el correo sea correcto
        valid_email = validate_email(email, check_deliverability=False)
        local_part = valid_email.local_part
        domain = valid_email.domain

        # Aplicar ofuscación a la parte local
        if len(local_part) <= obfuscated_length:
            obfuscated_local_part = local_part
        else:
            obfuscated_local_part = local_part[:obfuscated_length] + "*" * (
                    len(local_part) - obfuscated_length
            )

        return f"{obfuscated_local_part}@{domain}"
    except EmailNotValidError:
        # Si el correo no es válido, devolver el valor sin procesar
        logging.warning(f"Intento de ofuscar un correo inválido: {email}")
        return email


class EmailObfuscationFilter(logging.Filter):
    """
    Filtro de registro para ofuscar direcciones de correo electrónico.

    Este filtro examina los registros de logging en busca de campos de correo
    electrónico y aplica ofuscación para proteger la privacidad del usuario
    mientras mantiene el valor de diagnóstico. El nivel de ofuscación es
    configurable según el entorno.
    """
    def __init__(self, name: str = "", obfuscated_length: int = 2) -> None:
        super().__init__(name)
        self.obfuscated_length = obfuscated_length

    def filter(self, record: logging.LogRecord) -> bool:
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_length)
        return True


base_handlers = ["default", "rotating_file"]
sqlalchemy_handlers = ["seed_data_file"]


def configure_logging() -> None:
    """
    Maneja el registro de la aplicación.
    Configura los controladores, formateadores y filtros de logging.
    Se utilizan diferentes configuraciones para entornos de desarrollo
    y producción, incluyendo la ofuscación de direcciones de correo
    electrónico y la inclusión de ID de correlación en los registros.
    """
    log_dir = Path("app/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8 if isinstance(config, DevConfig) else 32,
                    "default_value": "-",
                },
                "email_obfuscation": {
                    "()": EmailObfuscationFilter,
                    "obfuscated_length": 2 if isinstance(config, DevConfig) else 0,
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "(%(correlation_id)s) %(name)s:%(lineno)d - %(message)s",
                },
                "access": {
                    "()": "uvicorn.logging.AccessFormatter",
                    "fmt": "%(levelprefix)s (%(correlation_id)s) %(client_addr)s - "
                           "%(request_line)s - %(status_code)s",
                    "use_colors": True,
                },
                "file": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(asctime)s %(msecs)03d %(levelname)s "
                              "%(correlation_id)s %(name)s %(lineno)d %(message)s",
                },
                "seed_data_file_formatter": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
                "access": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "access",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filters": ["correlation_id", "email_obfuscation"],
                    "filename": "app/logs/app.log",
                    "maxBytes": 1024 * 1024 * 5, # 5 MB
                    "backupCount": 5,
                    "encoding": "utf-8",
                },
                "seed_data_file": {
                    "class": "logging.FileHandler",
                    "level": "INFO",
                    "formatter": "seed_data_file_formatter",
                    "filename": "app/logs/seed_data.log",
                    "mode": "w", # Sobrescribe el archivo
                    "encoding": "utf-8",
                },
            },
            "loggers": {
                "__main__": {
                    "handlers": ["default"],
                    "level": "INFO",
                    "propagate": False,
                },
                "app": {
                    "handlers": base_handlers,
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["access", "rotating_file"],
                    "level": "INFO",
                },
                "sqlalchemy.engine": {
                    "handlers": sqlalchemy_handlers,
                    "level": "DEBUG" if isinstance(config, DevConfig) else "WARNING",
                    "propagate": False,
                },
            },
        },
    )
