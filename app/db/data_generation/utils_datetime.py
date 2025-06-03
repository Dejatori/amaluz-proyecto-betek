import logging

from datetime import datetime, timedelta
import random
from faker import Faker

# Configuración
logger = logging.getLogger(__name__)
fake = Faker("es_CO")

SIMULATION_START_DATE = datetime(2022, 1, 15, 0, 0, 0)
SIMULATION_END_DATE = datetime(2025, 4, 30, 23, 59, 59)
STORE_OPENING_DATE = datetime(2022, 1, 10, 0, 0, 0)
PRODUCTOS_START_DATE_LIMIT = datetime(2022, 1, 15, 0, 0, 0)
PRODUCTOS_END_DATE_LIMIT = datetime(2025, 4, 15, 23, 59, 59)


def generar_fecha_secuencial(
    fecha_inicio_rango: datetime,
    fecha_fin_rango: datetime,
    total_elementos: int,
    indice_actual: int,
) -> datetime:
    """
    Genera una fecha de forma secuencial dentro de un rango de fechas dado,
    distribuyendo los elementos uniformemente.

    Args:
        fecha_inicio_rango: La fecha de inicio del período.
        fecha_fin_rango: La fecha de fin del período.
        total_elementos: El número total de elementos a distribuir en el rango.
        indice_actual: El índice del elemento actual (basado en 0).

    Returns:
        La fecha calculada para el elemento actual.
    """
    if not isinstance(fecha_inicio_rango, datetime) or not isinstance(
        fecha_fin_rango, datetime
    ):
        raise TypeError("Las fechas de inicio y fin deben ser objetos datetime.")
    if total_elementos <= 0:
        raise ValueError("El total de elementos debe ser positivo.")
    if not (0 <= indice_actual < total_elementos):
        raise ValueError("El índice actual está fuera de rango.")
    if fecha_inicio_rango > fecha_fin_rango:
        raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin.")

    rango_total_segundos = (fecha_fin_rango - fecha_inicio_rango).total_seconds()

    if total_elementos == 1:
        # Si solo hay un elemento, puede ser la fecha de inicio o un promedio,
        # o simplemente la fecha de inicio para simplicidad.
        # Aquí se usa la fecha de inicio.
        paso_segundos = 0
    else:
        # Asegura que la división sea entre el número de intervalos, no de elementos.
        paso_segundos = rango_total_segundos / (total_elementos - 1)

    segundos_a_sumar = indice_actual * paso_segundos
    fecha_generada = fecha_inicio_rango + timedelta(seconds=segundos_a_sumar)

    # Asegurar que la fecha generada no exceda la fecha_fin_rango,
    # especialmente debido a posibles imprecisiones de punto flotante.
    return min(fecha_generada, fecha_fin_rango)


def get_random_datetime_in_range(
    min_date: datetime,
    max_date: datetime = None,
) -> datetime:
    """
    Genera una fecha aleatoria entre min_date y max_date.
    Si min_date > max_date, devuelve min_date + un pequeño incremento aleatorio.

    Args:
        min_date: La fecha mínima (inclusive)
        max_date: La fecha máxima (inclusive)

    Returns:
        Una fecha aleatoria dentro del rango especificado
    """
    # Validación de tipos
    if not isinstance(min_date, datetime) or not isinstance(max_date, datetime):
        raise TypeError("min_date y max_date deben ser objetos datetime")

    # Si la fecha mínima es posterior a la máxima, añadir un pequeño incremento aleatorio
    if min_date >= max_date:
        # Añadir entre 1 segundo y 5 minutos
        random_seconds = random.randint(1, 300)
        return min_date + timedelta(seconds=random_seconds)

    try:
        # Usar faker para generar una fecha aleatoria en el rango
        time_diff_seconds = int((max_date - min_date).total_seconds())
        random_seconds = random.randint(0, time_diff_seconds)
        return min_date + timedelta(seconds=random_seconds)
    except Exception as e:
        # En caso de error con faker, implementar fallback manual
        time_diff = (max_date - min_date).total_seconds()
        random_seconds = random.uniform(0, time_diff)
        return min_date + timedelta(seconds=random_seconds)


def get_random_datetime(
    min_date: datetime,
    max_date: datetime = None,
    base_date_for_delta: datetime = None,
    min_delta_seconds: int = 0,
    max_delta_seconds: int = 300,
) -> datetime:
    """
    Genera una fecha y hora aleatoria.
    - Si base_date_for_delta se proporciona, la fecha generada será
      base_date_for_delta + un delta aleatorio (entre min_delta_seconds y max_delta_seconds).
      La min_date sigue siendo una cota inferior.
    - Si no, genera una fecha entre min_date y max_date.
    - max_date por defecto es SIMULATION_END_DATE.
    """
    if max_date is None:
        max_date = SIMULATION_END_DATE

    if not isinstance(min_date, datetime):
        logger.error("min_date debe ser un objeto datetime.")
        # Considerar lanzar una excepción o devolver un valor por defecto seguro
        min_date = SIMULATION_START_DATE  # Fallback muy genérico
    if not isinstance(max_date, datetime):
        logger.error("max_date debe ser un objeto datetime.")
        max_date = SIMULATION_END_DATE  # Fallback

    # Asegurar que min_date no sea posterior a max_date
    if min_date > max_date:
        logger.warning(
            f"min_date {min_date} es posterior a max_date {max_date}. "
            f"Se usará min_date y se añadirá un pequeño delta si no hay base_date_for_delta, "
            f"o se intentará ajustar con base_date_for_delta."
        )
        if (
            not base_date_for_delta
        ):  # Si no hay base, solo podemos avanzar desde min_date
            # Añadir entre 1 segundo y 5 minutos, pero sin superar un max_date teórico si fuera relevante
            random_seconds_increment = random.randint(
                1, max_delta_seconds if max_delta_seconds > 0 else 300
            )
            candidate = min_date + timedelta(seconds=random_seconds_increment)
            return min(
                candidate, SIMULATION_END_DATE
            )  # Asegurar no pasar el fin de la simulación global
        # Si hay base_date_for_delta, la lógica de abajo intentará ajustarse. Max_date sigue siendo problemático.

    if base_date_for_delta:
        if not isinstance(base_date_for_delta, datetime):
            logger.error("base_date_for_delta debe ser un objeto datetime.")
            base_date_for_delta = min_date  # Fallback

        effective_base_date = max(base_date_for_delta, min_date)
        delta = timedelta(seconds=random.randint(min_delta_seconds, max_delta_seconds))
        candidate_date = effective_base_date + delta
        # Asegurar que la fecha candidata no exceda max_date y no sea anterior a min_date
        return min(max(candidate_date, min_date), max_date)

    # Generar entre min_date y max_date
    try:
        # Asegurar que los timestamps sean válidos para randint
        min_ts = int(min_date.timestamp())
        max_ts = int(max_date.timestamp())
        if min_ts > max_ts:  # Si después de todos los ajustes, sigue inválido
            logger.warning(
                f"Timestamp inválido: min_ts {min_ts} > max_ts {max_ts}. Usando min_date."
            )
            return min_date

        random_timestamp = random.randint(min_ts, max_ts)
        return datetime.fromtimestamp(random_timestamp)

    except OverflowError:
        logger.error(
            f"OverflowError con fechas: min_date={min_date}, max_date={max_date}"
        )
        return min(min_date, max_date)  # Devolver la más temprana como fallback
    except ValueError as e:  # Podría ocurrir si min_ts > max_ts
        logger.error(
            f"ValueError en randint para timestamps: {e}. min_date={min_date}, max_date={max_date}"
        )
        return min(min_date, max_date)


def generate_subsequent_update_datetime(
    previous_update_datetime: datetime,
    min_delta_seconds: int = 60,  # Al menos 1 minuto después
    max_delta_seconds: int = 3600 * 2,  # Hasta 2 horas después por defecto
    max_date_override: datetime = None,
) -> datetime:
    """Genera una fecha de actualización subsecuente, asegurando que sea posterior."""
    effective_max_date = max_date_override if max_date_override else SIMULATION_END_DATE
    # La nueva fecha debe ser estrictamente posterior a la anterior
    strict_min_date = previous_update_datetime + timedelta(seconds=1)

    return get_random_datetime(
        min_date=strict_min_date,
        max_date=effective_max_date,
        base_date_for_delta=previous_update_datetime,  # La base es la anterior
        min_delta_seconds=(
            min_delta_seconds if min_delta_seconds > 0 else 1
        ),  # Asegurar delta positivo
        max_delta_seconds=max_delta_seconds,
    )
