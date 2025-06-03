"""
Módulo para generación de datos de prueba relacionados con envíos.
Contiene funciones para crear envíos en la base de datos.
"""
import logging
import random
from datetime import datetime, timedelta
from decimal import Decimal

from faker import Faker
from sqlalchemy.orm import Session

from app.models import HistorialMetodosEnvio, Pedido
from app.models.envio import Envio, EstadoEnvioEnum

# Configuración
logger = logging.getLogger(__name__)
fake = Faker("es_CO")

# Empresas de envío predefinidas
EMPRESAS_ENVIO = [
    "Servientrega",
    "Interrapidísimo",
    "Coordinadora",
    "Deprisa",
    "TCC",
    "Envía"
]


def create_envio_for_pedido(
    db: Session, pedido: Pedido, fecha_pedido: datetime, usuario_id: int
) -> tuple[Envio, HistorialMetodosEnvio]:
    """
    Crea un envío asociado a un pedido específico y su historial de métodos de envío correspondiente.

    Args:
        db: Sesión de base de datos.
        pedido: Objeto Pedido al que se asociará el envío.
        fecha_pedido: Fecha del pedido (para mantener coherencia temporal).
        usuario_id: ID del usuario que realizó el pedido.

    Returns:
        Tupla con el envío creado y el historial de métodos de envío.
    """
    try:
        # Fecha de envío: unos segundos después de la creación del pedido
        fecha_envio = fecha_pedido + timedelta(seconds=random.randint(30, 120))

        # Fecha estimada de entrega: entre 2 y 14 días después
        fecha_entrega_estimada = fecha_envio + timedelta(days=random.randint(2, 14))

        # Costo de envío: entre 5000 y 20000
        costo_envio = Decimal(str(random.randint(5000, 20000)))

        # Generar nombre de la empresa de envío
        empresa_envio = fake.random_element(elements=EMPRESAS_ENVIO)

        # Crear el objeto envío
        nuevo_envio = Envio(
            pedido_id=pedido.id,
            empresa_envio=empresa_envio,
            numero_guia=f"GUIA-{random.randint(1000000, 9999999)}",
            costo_envio=costo_envio,
            fecha_envio=fecha_envio,
            fecha_entrega_estimada=fecha_entrega_estimada,
            estado_envio=EstadoEnvioEnum.Pendiente,
            fecha_registro=fecha_envio,
            fecha_actualizacion=fecha_envio,
        )

        db.add(nuevo_envio)
        db.flush()  # Para obtener el ID del envío

        # Crear el historial de métodos de envío
        nuevo_historial_envio = HistorialMetodosEnvio(
            usuario_id=usuario_id,
            empresa_envio=empresa_envio,
            costo_envio=costo_envio,
            fecha_registro=fecha_envio,
            fecha_actualizacion=fecha_envio,
        )

        db.add(nuevo_historial_envio)
        db.flush()

        return nuevo_envio, nuevo_historial_envio

    except Exception as e:
        logger.error(f"Error al crear envío para pedido {pedido.id}: {e}")
        raise


def update_envio_estado_y_fecha(
    db: Session,
    envio: Envio,
    nuevo_estado: EstadoEnvioEnum,
    fecha_actualizacion_envio: datetime,
) -> bool:
    """
    Actualiza el estado de un envío y su fecha de actualización.
    No realiza commit; debe ser manejado por la función que llama.

    Args:
        db: Sesión de base de datos.
        envio: Objeto Envio cuyo estado se actualizará.
        nuevo_estado: Nuevo estado del envío.
        fecha_actualizacion_envio: La nueva fecha de actualización para el envío.

    Returns:
        True si la actualización fue exitosa (añadido a la sesión), False en caso contrario.
    """
    if not envio:
        logger.warning("Se intentó actualizar un envío nulo.")
        return False
    try:
        envio.estado_envio = nuevo_estado
        envio.fecha_actualizacion = fecha_actualizacion_envio

        # Si el envío se marca como Entregado, actualizar fecha_entrega_real
        if nuevo_estado == EstadoEnvioEnum.Entregado:
            # Asegurarse que la fecha_entrega_real no sea anterior a la fecha_envio si existe
            if envio.fecha_envio and fecha_actualizacion_envio < envio.fecha_envio:
                logger.warning(
                    f"Fecha de entrega real {fecha_actualizacion_envio} es anterior a fecha de envío {envio.fecha_envio} para envío {envio.id}. Se usará la fecha de envío."
                )
                envio.fecha_entrega_real = envio.fecha_envio
            else:
                envio.fecha_entrega_real = fecha_actualizacion_envio

        # Si el envío se marca como Devuelto y no tiene fecha_entrega_real,
        # se podría considerar poner la fecha_actualizacion_envio como fecha_entrega_real
        # o dejarla null dependiendo de la lógica de negocio.
        # Por ahora, solo se actualiza para Entregado.

        db.add(envio)  # Añade a la sesión, pero no hace commit
        logger.info(
            f"Envío {envio.id} (pedido {envio.pedido_id}) programado para actualizar a estado {nuevo_estado} en fecha {fecha_actualizacion_envio.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return True
    except Exception as e:
        logger.error(
            f"Error al programar actualización del estado del envío {envio.id}: {e}",
            exc_info=True,
        )
        return False
