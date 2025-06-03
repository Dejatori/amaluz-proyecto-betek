"""
Módulo para generación de datos de prueba relacionados con los detalles de pedido.
Contiene funciones para crear detalles de pedido y actualizar los totales de los pedidos.
"""

import logging
import random
from datetime import timedelta, datetime
from decimal import Decimal

from faker import Faker
from sqlalchemy.orm import Session

from app.db.data_generation.comentarios import create_comentario
from app.db.data_generation.envios import update_envio_estado_y_fecha
from app.models import (
    Carrito,
    Pedido,
    Producto,
    DetallePedido,
    Inventario,
    Envio,
)
from app.models.envio import EstadoEnvioEnum
from app.models.pedido import EstadoPedidoEnum
from app.models.producto import EstadoProductoEnum

from app.db.data_generation.utils_datetime import (
    SIMULATION_END_DATE,
    generate_subsequent_update_datetime,
)
from app.db.data_generation.inventario import (
    actualizar_inventario_por_pedido,
    reponer_stock_tras_cancelacion,
)

# Configuración
logger = logging.getLogger(__name__)
fake = Faker("es_CO")

# --- Constantes para la actualización de estados de pedidos (adaptadas de pedidos.py) ---
MIN_SECONDS_ENTRE_ACTUALIZACIONES_DETALLE = 60 * 5  # 5 minutos
MAX_SECONDS_ENTRE_ACTUALIZACIONES_DETALLE = 60 * 60 * 6  # 6 horas

PORCENTAJE_CANCELACION_DETALLE = 0.05
PORCENTAJE_REEMBOLSO_DESDE_ENTREGADO_DETALLE = 0.03
PORCENTAJE_REEMBOLSO_DESDE_CANCELADO_DETALLE = 0.01

# --- Constantes para la generación de comentarios (adaptadas de pedidos.py) ---
PORCENTAJE_PEDIDOS_CON_COMENTARIOS_DETALLE = 0.7
MIN_DAYS_POST_ENTREGA_COMENTARIO_DETALLE = 0
MAX_DAYS_POST_ENTREGA_COMENTARIO_DETALLE = 7


# --- Funciones de utilidad para calcular fechas de transición (basadas en reglas) ---
# Estas funciones calculan las fechas objetivo para cada estado según las reglas.
def _calcular_fecha_procesando_simulacion(fecha_creacion_pedido: datetime) -> datetime:
    """Calcula la fecha para pasar a 'Procesando': 30-60 minutos después de la creación."""
    delta = timedelta(minutes=random.randint(30, 60))
    fecha_procesando = fecha_creacion_pedido + delta
    return min(fecha_procesando, SIMULATION_END_DATE)


def _calcular_fecha_envio_simulacion(
    fecha_creacion_pedido: datetime, fecha_referencia_anterior: datetime
) -> datetime:
    """Calcula la fecha para pasar a 'Enviado': 1-2 días desde creación, y después de la fecha anterior."""
    delta_dias = random.randint(1, 2)
    delta_segundos_adicionales = random.randint(
        0, (24 * 60 * 60) - 1
    )  # Añade variabilidad horaria
    fecha_envio = fecha_creacion_pedido + timedelta(
        days=delta_dias, seconds=delta_segundos_adicionales
    )
    # Asegurar que la fecha de envío sea posterior a la fecha del estado anterior (ej. Procesando)
    fecha_envio = max(fecha_envio, fecha_referencia_anterior + timedelta(seconds=1))
    return min(fecha_envio, SIMULATION_END_DATE)


def _calcular_fecha_entrega_simulacion(
    fecha_creacion_pedido: datetime, fecha_referencia_anterior: datetime
) -> datetime:
    """Calcula la fecha para pasar a 'Entregado': 4-10 días desde creación, y después de la fecha anterior."""
    delta_dias = random.randint(4, 10)
    delta_segundos_adicionales = random.randint(
        0, (24 * 60 * 60) - 1
    )  # Añade variabilidad horaria
    fecha_entrega = fecha_creacion_pedido + timedelta(
        days=delta_dias, seconds=delta_segundos_adicionales
    )
    # Asegurar que la fecha de entrega sea posterior a la fecha del estado anterior (ej. Enviado)
    fecha_entrega = max(fecha_entrega, fecha_referencia_anterior + timedelta(seconds=1))
    return min(fecha_entrega, SIMULATION_END_DATE)


def create_detalles_for_pedido(
    db: Session,
    pedido: Pedido,
    carritos_usuario: list[Carrito],
    fecha_creacion: datetime,
) -> Decimal:
    """
    Crea detalles de pedido basados en los ítems del carrito de un usuario,
    actualizando el inventario correspondiente.

    Args:
        db: Sesión de base de datos.
        pedido: Objeto Pedido al que se asociarán los detalles.
        carritos_usuario: Lista de ítems de carrito del usuario.
        fecha_creacion: Fecha en que se crean los detalles (debe ser coherente con el pedido).

    Returns:
        Decimal: El costo total bruto de los detalles creados (sin descuentos ni envío).
    """
    detalles_creados = []
    costo_total_bruto = Decimal("0.00")

    for carrito in carritos_usuario:
        producto = db.query(Producto).get(carrito.producto_id)
        if not producto:
            logger.warning(
                f"Producto {carrito.producto_id} no encontrado para carrito {carrito.id}"
            )
            continue

        # Verificar coherencia temporal
        if producto.fecha_registro > fecha_creacion:
            logger.warning(
                f"Incoherencia temporal: Producto {producto.id} registrado después del pedido {pedido.id}"
            )
            continue

        # Obtener la cantidad disponible en inventario
        inventario = (
            db.query(Inventario).filter(Inventario.producto_id == producto.id).first()
        )
        if not inventario:
            logger.warning(
                f"No hay registro de inventario para producto {producto.id} en pedido {pedido.id}"
            )
            continue

        cantidad_solicitada = carrito.cantidad
        cantidad_disponible = inventario.cantidad_disponible

        # Si no hay suficiente inventario, ajustar la cantidad al máximo disponible
        if cantidad_disponible <= 0:
            logger.warning(
                f"Inventario agotado para producto {producto.id} en pedido {pedido.id}. Saltando este detalle."
            )
            continue

        if cantidad_solicitada > cantidad_disponible:
            logger.info(
                f"Ajustando cantidad solicitada para producto {producto.id} en pedido {pedido.id}. "
                f"Solicitada: {cantidad_solicitada}, Disponible: {cantidad_disponible}. "
                f"Se usará la cantidad disponible."
            )
            cantidad = cantidad_disponible
        else:
            cantidad = cantidad_solicitada

        # Crear detalle de pedido usando la cantidad ajustada
        precio_unitario = producto.precio_venta
        subtotal = Decimal(cantidad) * precio_unitario

        detalle = DetallePedido(
            pedido_id=pedido.id,
            producto_id=producto.id,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            subtotal=subtotal,
            fecha_registro=fecha_creacion,
            fecha_actualizacion=fecha_creacion,
        )

        detalles_creados.append(detalle)
        costo_total_bruto += subtotal

    if detalles_creados:
        try:
            db.add_all(detalles_creados)
            db.flush()

            # --- INICIO: Simulación del ciclo de vida del pedido ---
            # El pedido está en estado 'Pendiente'.
            # pedido.fecha_actualizacion es igual a pedido.fecha_registro en este punto.

            pedido_fue_cancelado_simulado = False
            fecha_actual_del_pedido = (
                pedido.fecha_actualizacion
            )  # Para referencia en cálculos de fechas

            # 1. Intento de Cancelación (desde Pendiente)
            # Ocurre poco después de la creación, antes de la ventana de procesamiento.
            if random.random() < PORCENTAJE_CANCELACION_DETALLE:
                # Fecha de cancelación: entre 1 y 29 minutos después de la creación.
                # Usamos pedido.fecha_registro como base para la cancelación temprana.
                delta_cancelacion = timedelta(minutes=random.randint(1, 29))
                fecha_cancelacion_propuesta = pedido.fecha_registro + delta_cancelacion
                fecha_cancelacion_simulada = min(
                    fecha_cancelacion_propuesta, SIMULATION_END_DATE
                )

                if (
                    fecha_cancelacion_simulada > fecha_actual_del_pedido
                ):  # Asegurar que la fecha avance
                    if update_pedido_a_cancelado(
                        db, pedido, fecha_cancelacion_simulada, commit_directo=False
                    ):
                        pedido_fue_cancelado_simulado = True
                        fecha_actual_del_pedido = pedido.fecha_actualizacion

                        update_envio(
                            db,
                            pedido,
                            estado_envio=EstadoEnvioEnum.Incidencia,
                            fecha_actual_del_pedido=fecha_actual_del_pedido,
                        )

                        # La reposición de inventario se maneja dentro de update_pedido_a_cancelado

            # 2. Pendiente a Procesando (si no fue cancelado)
            if (
                not pedido_fue_cancelado_simulado
                and pedido.estado_pedido == EstadoPedidoEnum.Pendiente
            ):
                fecha_procesando_propuesta = _calcular_fecha_procesando_simulacion(
                    pedido.fecha_registro
                )
                if fecha_procesando_propuesta > fecha_actual_del_pedido:
                    if update_pedido_a_procesando(
                        db, pedido, fecha_procesando_propuesta, commit_directo=False
                    ):
                        fecha_actual_del_pedido = pedido.fecha_actualizacion

            # 3. Procesando a Enviado
            if pedido.estado_pedido == EstadoPedidoEnum.Procesando:
                fecha_envio_propuesta = _calcular_fecha_envio_simulacion(
                    pedido.fecha_registro, fecha_actual_del_pedido
                )
                if fecha_envio_propuesta > fecha_actual_del_pedido:
                    if update_pedido_a_enviado(
                        db, pedido, fecha_envio_propuesta, commit_directo=False
                    ):
                        fecha_actual_del_pedido = pedido.fecha_actualizacion

                        update_envio(
                            db,
                            pedido,
                            estado_envio=EstadoEnvioEnum.En_transito,
                            fecha_actual_del_pedido=fecha_actual_del_pedido,
                        )

            # 4. Enviado a Entregado
            if pedido.estado_pedido == EstadoPedidoEnum.Enviado:
                fecha_entrega_propuesta = _calcular_fecha_entrega_simulacion(
                    pedido.fecha_registro, fecha_actual_del_pedido
                )
                if fecha_entrega_propuesta > fecha_actual_del_pedido:
                    if update_pedido_a_entregado(
                        db, pedido, fecha_entrega_propuesta, commit_directo=False
                    ):
                        fecha_actual_del_pedido = pedido.fecha_actualizacion

                        # Actualizar el estado del envío asociado al pedido
                        update_envio(
                            db,
                            pedido,
                            estado_envio=EstadoEnvioEnum.Entregado,
                            fecha_actual_del_pedido=fecha_actual_del_pedido,
                        )

                        # Generar comentarios usando la nueva función
                        create_comentario(
                            db,
                            pedido,
                            fecha_entrega=fecha_actual_del_pedido,
                            porcentaje_comentario=PORCENTAJE_PEDIDOS_CON_COMENTARIOS_DETALLE,
                            min_days_post_entrega=0,
                            max_days_post_entrega=7,
                        )

            # 5. Reembolso (desde Entregado o Cancelado)
            # La fecha de reembolso es relativa al estado anterior inmediato.
            if (
                pedido.estado_pedido == EstadoPedidoEnum.Entregado
                and random.random() < PORCENTAJE_REEMBOLSO_DESDE_ENTREGADO_DETALLE
            ):
                fecha_reembolso_propuesta = generate_subsequent_update_datetime(
                    fecha_actual_del_pedido
                )  # Usa la fecha del estado anterior
                if fecha_reembolso_propuesta > fecha_actual_del_pedido:
                    if update_pedido_a_reembolsado(
                        db, pedido, fecha_reembolso_propuesta, commit_directo=False
                    ):
                        fecha_actual_del_pedido = pedido.fecha_actualizacion

                        update_envio(
                            db,
                            pedido,
                            estado_envio=EstadoEnvioEnum.Devuelto,
                            fecha_actual_del_pedido=fecha_actual_del_pedido,
                        )

            elif (
                pedido.estado_pedido == EstadoPedidoEnum.Cancelado
                and random.random() < PORCENTAJE_REEMBOLSO_DESDE_CANCELADO_DETALLE
            ):
                fecha_reembolso_propuesta = generate_subsequent_update_datetime(
                    fecha_actual_del_pedido
                )  # Usa la fecha del estado anterior
                if fecha_reembolso_propuesta > fecha_actual_del_pedido:
                    if update_pedido_a_reembolsado(
                        db, pedido, fecha_reembolso_propuesta, commit_directo=False
                    ):
                        fecha_actual_del_pedido = pedido.fecha_actualizacion

                        update_envio(
                            db,
                            pedido,
                            estado_envio=EstadoEnvioEnum.Devuelto,
                            fecha_actual_del_pedido=fecha_actual_del_pedido,
                        )

            # --- FIN: Simulación del ciclo de vida del pedido ---

            # Actualizar inventario para cada detalle creado (esto ya estaba)
            # La fecha_creacion aquí es la fecha_registro del pedido/detalle.
            for detalle_item in detalles_creados:
                # Solo se descuenta inventario si el pedido no fue cancelado durante esta simulación.
                # Si fue cancelado, el stock ya se repuso.
                if not pedido_fue_cancelado_simulado:
                    exito, inventario_actualizado = actualizar_inventario_por_pedido(
                        db, detalle_item, fecha_creacion
                    )
                    if not exito:
                        logger.warning(
                            f"No se pudo actualizar el inventario para detalle de pedido {detalle_item.id}"
                        )
                    elif (
                        inventario_actualizado
                        and inventario_actualizado.cantidad_disponible == 0
                    ):
                        producto_inv = db.query(Producto).get(detalle_item.producto_id)
                        if (
                            producto_inv
                            and producto_inv.estado != EstadoProductoEnum.Inactivo
                        ):
                            producto_inv.estado = EstadoProductoEnum.Inactivo
                            # La fecha de actualización del producto debe ser coherente.
                            # Usar la fecha_creacion del detalle/pedido o la fecha_actual_del_pedido si es posterior.
                            producto_inv.fecha_actualizacion = max(
                                fecha_creacion, fecha_actual_del_pedido
                            )
                            logger.info(
                                f"Producto {producto_inv.id} marcado como Inactivo por agotamiento de stock"
                            )

            # El commit final se realiza en la función que llama a create_detalles_for_pedido
            # (generalmente create_pedidos), lo cual es correcto para mantener la atomicidad.

            # logger.debug(f"Creados {len(detalles_creados)} detalles para el pedido {pedido.id}")
        except Exception as e:
            logger.error(
                f"Error al crear detalles y simular ciclo de vida para pedido asociado a los carritos: {e}",
                exc_info=True,
            )
            raise
    else:
        logger.warning(
            f"No se pudieron crear detalles para el pedido (lista de carritos vacía o productos no válidos)."
        )

    return costo_total_bruto


def update_pedido_a_procesando(
    db: Session,
    pedido: Pedido,
    fecha_procesando: datetime,
    commit_directo: bool = False,
) -> bool:
    """Actualiza el estado del pedido a Procesando."""
    if (
        pedido.estado_pedido == EstadoPedidoEnum.Pendiente
        and pedido.fecha_actualizacion < fecha_procesando <= SIMULATION_END_DATE
    ):
        pedido.estado_pedido = EstadoPedidoEnum.Procesando
        pedido.fecha_actualizacion = fecha_procesando
        logger.info(
            f"Pedido {pedido.id} transicionado a Procesando en {fecha_procesando}"
        )
        if commit_directo:
            db.commit()
        else:
            db.flush()
        return True
    return False


def update_pedido_a_cancelado(
    db: Session,
    pedido: Pedido,
    fecha_cancelacion: datetime,
    commit_directo: bool = False,
) -> bool:
    """Actualiza el estado del pedido a Cancelado y repone stock."""
    if (
        pedido.estado_pedido == EstadoPedidoEnum.Pendiente
        and pedido.fecha_actualizacion < fecha_cancelacion <= SIMULATION_END_DATE
    ):
        pedido.estado_pedido = EstadoPedidoEnum.Cancelado
        pedido.fecha_actualizacion = fecha_cancelacion
        logger.info(
            f"Pedido {pedido.id} transicionado a Cancelado en {fecha_cancelacion}"
        )

        if pedido.detalles:  # Asegurarse que la relación esté cargada
            for detalle_item in pedido.detalles:
                exito_reposicion, _ = reponer_stock_tras_cancelacion(
                    db,
                    detalle_item.producto_id,
                    detalle_item.cantidad,
                    fecha_cancelacion,
                )
                if not exito_reposicion:
                    logger.error(
                        f"Fallo al reponer stock para producto {detalle_item.producto_id} tras cancelación del pedido {pedido.id}"
                    )
            logger.info(f"Inventario repuesto para pedido cancelado {pedido.id}")
        else:
            logger.warning(
                f"No se pudo reponer inventario para pedido cancelado {pedido.id} porque pedido.detalles no está disponible."
            )

        if commit_directo:
            db.commit()
        else:
            db.flush()
        return True
    return False


def update_pedido_a_enviado(
    db: Session, pedido: Pedido, fecha_envio: datetime, commit_directo: bool = False
) -> bool:
    """Actualiza el estado del pedido a Enviado."""
    if (
        pedido.estado_pedido == EstadoPedidoEnum.Procesando
        and pedido.fecha_actualizacion < fecha_envio <= SIMULATION_END_DATE
    ):
        pedido.estado_pedido = EstadoPedidoEnum.Enviado
        pedido.fecha_actualizacion = fecha_envio
        logger.info(f"Pedido {pedido.id} transicionado a Enviado en {fecha_envio}")

        if commit_directo:
            db.commit()
        else:
            db.flush()
        return True
    return False


def update_pedido_a_entregado(
    db: Session, pedido: Pedido, fecha_entrega: datetime, commit_directo: bool = False
) -> bool:
    """Actualiza el estado del pedido a Entregado."""
    if (
        pedido.estado_pedido == EstadoPedidoEnum.Enviado
        and pedido.fecha_actualizacion < fecha_entrega <= SIMULATION_END_DATE
    ):
        pedido.estado_pedido = EstadoPedidoEnum.Entregado
        pedido.fecha_actualizacion = fecha_entrega
        logger.info(f"Pedido {pedido.id} transicionado a Entregado en {fecha_entrega}")
        if commit_directo:
            db.commit()
        else:
            db.flush()
        return True
    return False


def update_pedido_a_reembolsado(
    db: Session, pedido: Pedido, fecha_reembolso: datetime, commit_directo: bool = False
) -> bool:
    """Actualiza el estado del pedido a Reembolsado."""
    if (
        pedido.estado_pedido in [EstadoPedidoEnum.Entregado, EstadoPedidoEnum.Cancelado]
        and pedido.fecha_actualizacion < fecha_reembolso <= SIMULATION_END_DATE
    ):
        estado_anterior = pedido.estado_pedido.value
        pedido.estado_pedido = EstadoPedidoEnum.Reembolsado
        pedido.fecha_actualizacion = fecha_reembolso
        logger.info(
            f"Pedido {pedido.id} ({estado_anterior}) transicionado a Reembolsado en {fecha_reembolso}"
        )
        if commit_directo:
            db.commit()
        else:
            db.flush()
        return True
    return False


def update_envio(
    db: Session,
    pedido: Pedido,
    estado_envio: EstadoEnvioEnum,
    fecha_actual_del_pedido: datetime,
):
    # Obtener el envío asociado al pedido
    envio = db.query(Envio).filter(Envio.pedido_id == pedido.id).first()

    if envio:
        # Actualizar el estado del envío y la fecha de entrega real
        update_envio_estado_y_fecha(
            db,
            envio,
            nuevo_estado=estado_envio,
            fecha_actualizacion_envio=fecha_actual_del_pedido,
        )
    else:
        logger.warning(f"No se encontró envío para el pedido {pedido.id}")
