"""
Módulo para generación de datos de prueba relacionados con descuentos.
Contiene funciones para crear descuentos en la base de datos.
"""

import logging
import random
import string
from datetime import timedelta, datetime
from typing import List, Optional, Any

from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import Descuento
from app.models.descuento import Descuento, EstadoDescuentoEnum
from app.db.data_generation.utils_datetime import get_random_datetime_in_range

# Configuración
logger = logging.getLogger(__name__)
fake = Faker("es_CO")

# Constantes globales para límites temporales
SIMULATION_START_DATE = datetime(2022, 2, 1)
SIMULATION_END_DATE = datetime(2025, 5, 1)

# Constantes para generación de descuentos
MIN_DISCOUNT_PERCENTAGE = 10
MAX_DISCOUNT_PERCENTAGE = 50
MIN_DISCOUNT_DURATION_DAYS = 3
MAX_DISCOUNT_DURATION_DAYS = 7
MAX_DAYS_BEFORE_START_FOR_REGISTRATION = (
    30  # Máximo de días antes de la fecha de inicio para registrar el descuento
)

# Fechas de descuentos
FECHAS_DESCUENTOS = {
    # 2022
    "san_valentin_2022": datetime(2022, 2, 14),
    "san_jose_2022": datetime(2022, 3, 21),
    "semana_santa_2022": datetime(2022, 4, 14),
    "dia_trabajo_2022": datetime(2022, 5, 1),
    "dia_madre_2022": datetime(2022, 5, 8),
    "ascension_2022": datetime(2022, 6, 13),
    "dia_padre_2022": datetime(2022, 6, 19),
    "independencia_2022": datetime(2022, 7, 20),
    "dia_amor_y_amistad_2022": datetime(2022, 9, 19),
    "halloween_2022": datetime(2022, 10, 31),
    "black_friday_2022": datetime(2022, 11, 25),
    "cyber_monday_2022": datetime(2022, 11, 28),
    "dia_velitas_2022": datetime(2022, 12, 7),
    "navidad_2022": datetime(2022, 12, 24),
    "fin_año_2022": datetime(2022, 12, 31),
    # 2023
    "año_nuevo_2023": datetime(2023, 1, 1),
    "reyes_magos_2023": datetime(2023, 1, 9),
    "san_valentin_2023": datetime(2023, 2, 14),
    "dia_de_la_mujer_2023": datetime(2023, 3, 8),
    "san_jose_2023": datetime(2023, 3, 20),
    "semana_santa_2023": datetime(2023, 4, 6),
    "dia_trabajo_2023": datetime(2023, 5, 1),
    "dia_madre_2023": datetime(2023, 5, 14),
    "ascension_2023": datetime(2023, 5, 29),
    "dia_del_padre_2023": datetime(2023, 6, 18),
    "independencia_2023": datetime(2023, 7, 20),
    "dia_amor_y_amistad_2023": datetime(2023, 9, 18),
    "halloween_2023": datetime(2023, 10, 31),
    "black_friday_2023": datetime(2023, 11, 24),
    "cyber_monday_2023": datetime(2023, 11, 27),
    "dia_velitas_2023": datetime(2023, 12, 7),
    "navidad_2023": datetime(2023, 12, 24),
    "fin_año_2023": datetime(2023, 12, 31),
    # 2024
    "año_nuevo_2024": datetime(2024, 1, 1),
    "reyes_magos_2024": datetime(2024, 1, 8),
    "san_valentin_2024": datetime(2024, 2, 14),
    "dia_de_la_mujer_2024": datetime(2024, 3, 8),
    "san_jose_2024": datetime(2024, 3, 18),
    "semana_santa_2024": datetime(2024, 3, 28),
    "dia_trabajo_2024": datetime(2024, 5, 1),
    "dia_madre_2024": datetime(2024, 5, 12),
    "ascension_2024": datetime(2024, 6, 17),
    "dia_del_padre_2024": datetime(2024, 6, 16),
    "independencia_2024": datetime(2024, 7, 20),
    "dia_amor_y_amistad_2024": datetime(2024, 9, 16),
    "halloween_2024": datetime(2024, 10, 31),
    "black_friday_2024": datetime(2024, 11, 29),
    "cyber_monday_2024": datetime(2024, 12, 2),
    "dia_velitas_2024": datetime(2024, 12, 7),
    "navidad_2024": datetime(2024, 12, 24),
    "fin_año_2024": datetime(2024, 12, 31),
    # 2025
    "año_nuevo_2025": datetime(2025, 1, 1),
    "reyes_magos_2025": datetime(2025, 1, 6),
    "san_valentin_2025": datetime(2025, 2, 14),
    "dia_de_la_mujer_2025": datetime(2025, 3, 8),
    "san_jose_2025": datetime(2025, 3, 17),
    "semana_santa_2025": datetime(2025, 4, 17),
    "dia_trabajo_2025": datetime(2025, 5, 1),
}


def generar_codigo_descuento(prefijo: str = "") -> str:
    """
    Genera un código de descuento único con un prefijo opcional.

    Args:
        prefijo: Prefijo opcional para el código (ej. NAVIDAD, CYBER, etc.)

    Returns:
        Código de descuento único
    """
    if prefijo:
        prefijo = f"{prefijo}_"

    # Generar código aleatorio de 6 caracteres alfanuméricos
    caracteres = string.ascii_uppercase + string.digits
    codigo_aleatorio = "".join(random.choice(caracteres) for _ in range(6))

    return f"{prefijo}{codigo_aleatorio}"


def generate_discount_dates(
    reference_date: Optional[datetime] = None,
    min_start_date: Optional[datetime] = None,
    max_end_date: Optional[datetime] = None,
) -> tuple[datetime, datetime, datetime]:
    """
    Genera fechas coherentes para un descuento:
    - fecha_registro: Entre SIMULATION_START_DATE y fecha_inicio (preferiblemente cercana a fecha_inicio)
    - fecha_inicio: Entre min_start_date y max_end_date
    - fecha_fin: Entre fecha_inicio y max_end_date

    Args:
        reference_date: Fecha de referencia para centrar el descuento (ej. fecha de un festivo)
        min_start_date: Fecha mínima para iniciar el descuento
        max_end_date: Fecha máxima para finalizar el descuento

    Returns:
        Tupla con (fecha_registro, fecha_inicio, fecha_fin)
    """
    # Establecer límites por defecto si no se proporcionan
    if min_start_date is None:
        min_start_date = SIMULATION_START_DATE

    if max_end_date is None:
        max_end_date = SIMULATION_END_DATE

    # Si se proporciona una fecha de referencia, crear un descuento alrededor de esa fecha
    if reference_date:
        # El descuento comienza entre 7 y 14 días antes de la fecha de referencia
        dias_antes = random.randint(7, 14)
        fecha_inicio = max(min_start_date, reference_date - timedelta(days=dias_antes))

        # El descuento termina entre 1 y 3 días después de la fecha de referencia
        dias_despues = random.randint(1, 3)
        fecha_fin = min(max_end_date, reference_date + timedelta(days=dias_despues))
    else:
        # Crear un descuento con fechas aleatorias dentro de los límites
        max_possible_start = max_end_date - timedelta(
            days=1
        )  # Al menos 1 día de duración
        if max_possible_start < min_start_date:
            # En caso de que el rango sea inválido, ajustamos
            fecha_inicio = min_start_date
            fecha_fin = max_end_date
        else:
            fecha_inicio = get_random_datetime_in_range(
                min_start_date, max_possible_start
            )

            # Aseguramos una duración mínima de 1 día
            min_end_date = fecha_inicio + timedelta(days=1)
            duracion_dias = random.randint(1, MAX_DISCOUNT_DURATION_DAYS)
            fecha_fin = min(fecha_inicio + timedelta(days=duracion_dias), max_end_date)

    # La fecha de registro es anterior a la fecha de inicio (entre 0 y MAX_DAYS_BEFORE_START_FOR_REGISTRATION días antes)
    dias_antes_registro = random.randint(0, MAX_DAYS_BEFORE_START_FOR_REGISTRATION)
    fecha_registro_tentativa = fecha_inicio - timedelta(days=dias_antes_registro)

    # Asegurar que la fecha de registro no sea anterior al inicio de la simulación
    fecha_registro = max(SIMULATION_START_DATE, fecha_registro_tentativa)

    # Si por alguna razón la fecha_registro resulta posterior a fecha_inicio, igualarla a fecha_inicio
    if fecha_registro > fecha_inicio:
        fecha_registro = fecha_inicio

    # Verificación final para garantizar que fecha_fin > fecha_inicio
    if fecha_fin <= fecha_inicio:
        fecha_fin = fecha_inicio + timedelta(days=1)

    return fecha_registro, fecha_inicio, fecha_fin


def create_descuentos(db: Session) -> List[Descuento]:
    """
    Crea descuentos con coherencia temporal.

    Args:
        db: Sesión de base de datos

    Returns:
        Lista de descuentos creados
    """
    # Lista para almacenar los descuentos creados y confirmados en la base de datos
    committed_descuentos = []

    # Fecha actual para comparar estados
    fecha_actual = datetime.now()

    # Fecha de registro base para asegurar secuencia cronológica
    ultima_fecha_registro = SIMULATION_START_DATE

    try:
        # Generar descuentos para fechas específicas
        for festivo_nombre, festivo_fecha in sorted(
            FECHAS_DESCUENTOS.items(), key=lambda x: x[1]
        ):
            # Verificar si el festivo está dentro del periodo de simulación
            if SIMULATION_START_DATE <= festivo_fecha <= SIMULATION_END_DATE:
                try:
                    # Generar fechas para el descuento del festivo
                    fecha_registro, fecha_inicio, fecha_fin = generate_discount_dates(
                        reference_date=festivo_fecha
                    )

                    # Asegurar que la fecha de registro sea posterior a la última registrada
                    fecha_registro = max(
                        fecha_registro, ultima_fecha_registro + timedelta(minutes=1)
                    )
                    ultima_fecha_registro = fecha_registro

                    # Generar datos del descuento
                    codigo = generar_codigo_descuento(
                        festivo_nombre.split("_")[0].upper()
                    )
                    porcentaje = random.randint(
                        MIN_DISCOUNT_PERCENTAGE, MAX_DISCOUNT_PERCENTAGE
                    )

                    # Determinar estado basado solo en la fecha de fin y la fecha actual
                    estado = (
                        EstadoDescuentoEnum.Inactivo
                        if fecha_fin < fecha_actual
                        else EstadoDescuentoEnum.Activo
                    )

                    # Crear el descuento
                    descuento = Descuento(
                        codigo_descuento=codigo,
                        porcentaje=porcentaje,
                        fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_fin,
                        estado=estado,
                        fecha_registro=fecha_registro,
                        # Fecha de actualización igual a fecha de registro al crear
                        fecha_actualizacion=fecha_registro,
                    )

                    db.add(descuento)
                    db.flush()  # Para obtener el ID asignado
                    committed_descuentos.append(descuento)

                except Exception as e:
                    logger.warning(
                        f"Error al crear descuento para {festivo_nombre}: {str(e)}"
                    )
                    continue

        # Confirmar todos los cambios en la base de datos
        db.commit()
        logger.info(f"Creados y confirmados {len(committed_descuentos)} descuentos.")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de SQLAlchemy al crear descuentos: {str(e)}")
        committed_descuentos = []
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear descuentos: {str(e)}")
        committed_descuentos = []

    return committed_descuentos


def get_descuentos(db: Session) -> list[Any] | list[type[Descuento]]:
    """
    Obtiene todos los descuentos activos e inactivos de la base de datos.

    Args:
        db: Sesión de base de datos

    Returns:
        Lista de descuentos
    """
    try:
        descuentos = db.query(Descuento).all()
        logger.info(f"Total de descuentos obtenidos: {len(descuentos)}.")
        return descuentos
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener descuentos: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error inesperado al obtener descuentos: {str(e)}")
        return []
