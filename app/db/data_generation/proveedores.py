# app/db/data_generation/proveedores.py
"""
Módulo para generación de datos de prueba relacionados con proveedores.
Contiene funciones para crear y actualizar proveedores en la base de datos.
"""
import logging
import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy.orm import Session

from app.models.proveedor import Proveedor

# Configuración
logger = logging.getLogger(__name__)
fake = Faker("es_CO")  # Usar localización para datos más realistas

PROVEEDORES_START_DATE_LIMIT = datetime(2022, 1, 5)
PROVEEDORES_END_DATE_LIMIT = datetime(2024, 11, 10, 23, 59, 59)


def create_proveedores(db: Session, count: int) -> list[Proveedor]:
    """
    Crea múltiples proveedores con datos ficticios y fechas de registro secuenciales.
    """
    proveedores_creados = []

    total_seconds_proveedores = (
        PROVEEDORES_END_DATE_LIMIT - PROVEEDORES_START_DATE_LIMIT
    ).total_seconds()
    if count <= 1:
        step_seconds_proveedores = 0
    else:
        step_seconds_proveedores = total_seconds_proveedores / (count - 1)

    for i in range(count):
        if i == 0:
            # El primer proveedor tiene exactamente la fecha de inicio
            fecha_registro_proveedor = PROVEEDORES_START_DATE_LIMIT
        else:
            # Para los demás proveedores, usar la lógica existente con variación aleatoria
            fecha_registro_proveedor = PROVEEDORES_START_DATE_LIMIT + timedelta(
                seconds=step_seconds_proveedores * i
                        + random.uniform(
                    0, step_seconds_proveedores if step_seconds_proveedores > 0 else 60
                )
            )
            # Asegurar que la fecha no sea mayor al límite
            if fecha_registro_proveedor > PROVEEDORES_END_DATE_LIMIT:
                fecha_registro_proveedor = PROVEEDORES_END_DATE_LIMIT - timedelta(days=random.randint(1, 3))

        nuevo_proveedor = Proveedor(
            nombre=fake.company(),
            telefono=fake.numerify(text="3##########"),
            direccion=fake.address(),
            fecha_registro=fecha_registro_proveedor,
            fecha_actualizacion=fecha_registro_proveedor,  # Inicialmente igual a fecha_registro
        )
        proveedores_creados.append(nuevo_proveedor)

    if proveedores_creados:
        db.add_all(proveedores_creados)
        db.commit()
        for prov in proveedores_creados:
            db.refresh(
                prov
            )  # Para obtener IDs y valores por defecto de la BD si es necesario
        logger.info(f"Creados {len(proveedores_creados)} proveedores.")
    else:
        logger.info("No se crearon proveedores.")

    return proveedores_creados
