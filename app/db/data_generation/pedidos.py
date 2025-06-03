"""
Módulo para generación de datos de prueba relacionados con pedidos.
Contiene funciones para crear y actualizar pedidos en la base de datos.
"""

import logging
import random
import uuid
from datetime import timedelta, datetime
from decimal import Decimal
from typing import Any, List

from faker import Faker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Pedido,
    Usuario,
    Carrito,
    Descuento,
    HistorialDescuento,
)
from app.models.pedido import EstadoPedidoEnum, MetodoPagoEnum

from app.db.data_generation.utils_datetime import (
    get_random_datetime_in_range,
    SIMULATION_END_DATE,
)
from app.db.data_generation.localizacion_pedido import create_localizacion_for_user
from app.db.data_generation.detalle_pedido import create_detalles_for_pedido
from app.db.data_generation.envios import create_envio_for_pedido

# Configuración
logger = logging.getLogger(__name__)
fake = Faker("es_CO")

def generate_pedido_codigo(timestamp_dt: datetime, counter: int) -> str:
    """Genera un código de pedido único."""
    return f"PED-{timestamp_dt.strftime('%Y%m%d%H%M%S')}-{counter}-{uuid.uuid4().hex[:4].upper()}"


def create_pedidos(
    db: Session,
    todos_los_descuentos: List[Descuento],
    carritos: List[Carrito],
    porcentaje_conversion: float = random.uniform(
        0.6, 0.9
    ),  # Porcentaje de carritos que se convertirán en pedidos
) -> List[Pedido]:
    """
    Crea pedidos basados en registros de carrito existentes de forma secuencial.
    Solo un porcentaje de los carritos se convierten en pedidos (los demás se consideran "abandonados").
    Mantiene coherencia temporal procesando los carritos en orden cronológico.

    Args:
        db: Sesión de base de datos.
        todos_los_descuentos: Lista de descuentos disponibles.
        carritos: Lista de carritos disponibles para convertir en pedidos.
        porcentaje_conversion: Porcentaje de carritos que se convertirán en pedidos (0.0-1.0).

    Returns:
        Lista de pedidos creados.
    """
    pedidos_creados_list: List[Pedido] = []

    if not carritos:
        logger.warning("No hay registros de carrito para crear pedidos.")
        return []

    # Ordenar TODOS los carritos por fecha_actualizacion (secuencia temporal global)
    carritos_ordenados = sorted(carritos, key=lambda c: c.fecha_actualizacion)

    # Agrupar carritos del mismo usuario en "sesiones de compra" (intervalo cercano)
    # Una "sesión de compra" serán todos los carritos de un usuario en un intervalo de 15 minutos
    sesiones_compra = []
    carritos_por_usuario = {}

    # Primera pasada: agrupar carritos por usuario
    for carrito in carritos_ordenados:
        if carrito.usuario_id not in carritos_por_usuario:
            carritos_por_usuario[carrito.usuario_id] = []
        carritos_por_usuario[carrito.usuario_id].append(carrito)

    # Segunda pasada: agrupar carritos en sesiones por tiempo
    for usuario_id, carritos_usuario in carritos_por_usuario.items():
        # Ordenar los carritos de este usuario específicamente por fecha
        carritos_usuario.sort(key=lambda c: c.fecha_actualizacion)

        grupo_actual = []
        for i, carrito in enumerate(carritos_usuario):
            if not grupo_actual:
                # Primer carrito del grupo
                grupo_actual.append(carrito)
            else:
                # Verificar si este carrito está dentro del intervalo temporal del grupo
                ultimo_carrito = grupo_actual[-1]
                intervalo = (carrito.fecha_actualizacion - ultimo_carrito.fecha_actualizacion).total_seconds() / 60.0

                if intervalo <= 15.0:  # 15 minutos como máximo entre carrito
                    # Este carrito pertenece a la misma sesión
                    grupo_actual.append(carrito)
                else:
                    # Este carrito inicia una nueva sesión
                    if len(grupo_actual) >= 1:
                        sesiones_compra.append(grupo_actual.copy())
                    grupo_actual = [carrito]

            # Si es el último carrito del usuario y hay un grupo en proceso
            if i == len(carritos_usuario) - 1 and grupo_actual:
                sesiones_compra.append(grupo_actual.copy())

    # Ordenar las sesiones por la fecha del último carrito de cada sesión
    sesiones_compra.sort(key=lambda grupo: max(c.fecha_actualizacion for c in grupo))

    # Determinar cuántas sesiones de compra se convertirán en pedidos
    num_sesiones_a_convertir = max(1, int(len(sesiones_compra) * porcentaje_conversion))
    logger.info(f"Se identificaron {len(sesiones_compra)} sesiones de compra distintas.")
    logger.info(f"Se convertirán aproximadamente {num_sesiones_a_convertir} sesiones en pedidos.")

    # Inicializar un contador para registrar cuántas sesiones se han evaluado
    contador_procesados = 0

    # Procesamos secuencialmente cada sesión de compra
    for grupo_carritos in sesiones_compra:
        contador_procesados += 1

        # Decisión aleatoria si esta sesión se convierte en pedido o se abandona
        sesiones_restantes = len(sesiones_compra) - contador_procesados
        pedidos_restantes = num_sesiones_a_convertir - len(pedidos_creados_list)

        if pedidos_restantes <= 0:
            # Ya creamos suficientes pedidos
            break

        # Calculamos la probabilidad dinámica para esta sesión
        if sesiones_restantes > 0:
            probabilidad_conversion = pedidos_restantes / sesiones_restantes
        else:
            probabilidad_conversion = 1.0  # Es la última sesión y aún necesitamos pedidos

        # Decisión aleatoria usando la probabilidad calculada
        if random.random() > probabilidad_conversion:
            # Esta sesión se considera "abandonada"
            continue

        try:
            # Usamos el primer carrito del grupo para obtener datos comunes
            primer_carrito = grupo_carritos[0]
            usuario_id = primer_carrito.usuario_id
            usuario_seleccionado = db.query(Usuario).get(usuario_id)

            if not usuario_seleccionado:
                logger.warning(f"No se encontró el usuario con ID {usuario_id}. Saltando.")
                continue

            # Usamos la fecha del último carrito como base para la secuencia temporal
            ultimo_carrito = grupo_carritos[-1]
            ultima_fecha_carrito = ultimo_carrito.fecha_actualizacion

            # --- PASO 1: Creación de Localización del Pedido ---
            # La localización debe ser 1-3 minutos después del carrito (reducimos el intervalo)
            min_fecha_localizacion = ultima_fecha_carrito + timedelta(minutes=1)
            max_fecha_localizacion = ultima_fecha_carrito + timedelta(minutes=3)

            if max_fecha_localizacion >= SIMULATION_END_DATE:
                logger.debug(f"Fecha de localización excede límite para sesión del usuario {usuario_id}. Ajustando.")
                max_fecha_localizacion = SIMULATION_END_DATE - timedelta(minutes=10)
                if min_fecha_localizacion >= max_fecha_localizacion:
                    logger.warning(f"No hay ventana temporal válida para sesión del usuario {usuario_id}. Saltando.")
                    continue

            localizacion_creada = create_localizacion_for_user(
                db,
                usuario_seleccionado,
                max_fecha_localizacion,
                fecha_minima=min_fecha_localizacion,  # Aseguramos que la fecha sea posterior al carrito
            )

            if localizacion_creada is None:
                logger.warning(f"No se pudo crear localización para sesión del usuario {usuario_id}. Saltando.")
                continue

            # --- PASO 2: Creación del Pedido ---
            # El pedido debe crearse 1-3 minutos después de la localización (reducimos el intervalo)
            min_fecha_pedido = localizacion_creada.fecha_registro + timedelta(minutes=1)
            max_fecha_pedido = localizacion_creada.fecha_registro + timedelta(minutes=3)

            if max_fecha_pedido >= SIMULATION_END_DATE:
                logger.debug(f"Fecha de pedido excede límite para sesión del usuario {usuario_id}. Ajustando.")
                max_fecha_pedido = SIMULATION_END_DATE - timedelta(minutes=5)
                if min_fecha_pedido >= max_fecha_pedido:
                    db.delete(localizacion_creada)
                    db.commit()
                    logger.warning(f"No hay ventana temporal válida para pedido de usuario {usuario_id}. Saltando.")
                    continue

            fecha_pedido_definitiva = get_random_datetime_in_range(
                min_fecha_pedido, max_fecha_pedido
            )

            # --- PASO 3: Aplicar descuento (si corresponde) ---
            descuento_aplicado_al_pedido = None
            if todos_los_descuentos:
                # Verificar descuentos vigentes en la fecha del pedido
                descuentos_validos = [
                    d
                    for d in todos_los_descuentos
                    if d.fecha_inicio <= fecha_pedido_definitiva <= d.fecha_fin
                ]

                if descuentos_validos:
                    # Verificar si el usuario ya usó alguno de estos descuentos
                    descuentos_no_usados = [
                        d
                        for d in descuentos_validos
                        if db.query(HistorialDescuento)
                        .filter_by(usuario_id=usuario_id, descuento_id=d.id)
                        .first()
                        is None
                    ]

                    # 70-90% de probabilidad de usar un descuento disponible
                    if descuentos_no_usados and random.random() < random.uniform(
                        0.75, 0.95
                    ):
                        descuento_aplicado_al_pedido = random.choice(
                            descuentos_no_usados
                        )

            # --- PASO 4: Crear el pedido y sus detalles ---
            codigo_pedido_str = generate_pedido_codigo(
                fecha_pedido_definitiva, len(pedidos_creados_list) + 1
            )
            nuevo_pedido = Pedido(
                usuario_id=usuario_id,
                id_localizacion=localizacion_creada.id,
                codigo_pedido=codigo_pedido_str,
                costo_total=Decimal("0.00"),  # Se actualizará después
                metodo_pago=random.choice(list(MetodoPagoEnum)),
                estado_pedido=EstadoPedidoEnum.Pendiente,
                fecha_registro=fecha_pedido_definitiva,
                fecha_actualizacion=fecha_pedido_definitiva,
            )
            db.add(nuevo_pedido)
            db.flush()  # Para obtener el ID del pedido

            # --- PASO 5: Crear envío para este pedido ---
            nuevo_envio, nuevo_historial_envio = create_envio_for_pedido(
                db=db,
                pedido=nuevo_pedido,
                fecha_pedido=fecha_pedido_definitiva,
                usuario_id=usuario_id,
            )

            # Obtener el costo del envío para incluirlo en el costo total
            costo_envio = nuevo_envio.costo_envio

            # --- PASO 6: Crear detalles del pedido basados en TODOS los carritos de la sesión ---
            # Aquí usamos todos los carritos del grupo como parte del mismo pedido
            costo_total_bruto = create_detalles_for_pedido(
                db=db,
                pedido=nuevo_pedido,
                carritos_usuario=grupo_carritos,
                fecha_creacion=fecha_pedido_definitiva,
            )

            if costo_total_bruto == Decimal("0.00"):
                logger.warning(
                    f"Pedido {nuevo_pedido.id} tiene costo total cero. Cancelando."
                )
                if nuevo_envio:
                    db.delete(nuevo_envio)
                if nuevo_historial_envio:
                    db.delete(nuevo_historial_envio)
                if localizacion_creada:
                    db.delete(localizacion_creada)
                db.rollback() # revierte el pedido y detalles también
                continue

            # --- PASO 7: Aplicar descuento y finalizar pedido ---
            costo_final_pedido = costo_total_bruto + costo_envio

            if descuento_aplicado_al_pedido:
                monto_descuento = costo_total_bruto * (
                    descuento_aplicado_al_pedido.porcentaje / Decimal("100.0")
                )
                costo_final_pedido = costo_total_bruto - monto_descuento + costo_envio

                # Registrar uso del descuento
                hist_desc = HistorialDescuento(
                    usuario_id=usuario_id,
                    descuento_id=descuento_aplicado_al_pedido.id,
                    fecha_registro=fecha_pedido_definitiva,
                    fecha_actualizacion=fecha_pedido_definitiva,
                )
                db.add(hist_desc)

            nuevo_pedido.costo_total = costo_final_pedido
            nuevo_pedido.fecha_actualizacion = fecha_pedido_definitiva + timedelta(
                seconds=random.randint(10, 60)
            )

            # Commit para guardar los cambios
            db.commit()
            pedidos_creados_list.append(nuevo_pedido)

            # Log cada 10 pedidos para no saturar la salida
            if len(pedidos_creados_list) % 10 == 0:
                logger.info(f"Progreso: {len(pedidos_creados_list)} pedidos creados. "
                            f"Último pedido: {nuevo_pedido.codigo_pedido} con {len(grupo_carritos)} productos")

        except IntegrityError as ie:
            logger.error(f"Error de integridad creando pedido para usuario {usuario_id}: {ie}")
            db.rollback()
        except SQLAlchemyError as sqlae:
            logger.error(f"Error SQLAlchemy creando pedido para usuario {usuario_id}: {sqlae}")
            db.rollback()
        except Exception as e:
            logger.error(f"Error inesperado creando pedido para usuario {usuario_id}: {e}", exc_info=True)
            db.rollback()

    logger.info(f"Proceso de creación de pedidos finalizado. Creados {len(pedidos_creados_list)} pedidos.")
    return pedidos_creados_list


def get_pedidos_entregados(db: Session) -> list[Any] | list[type[Pedido]]:
    """
    Obtiene todos los pedidos que están en estado 'Entregado'.

    Args:
        db: Sesión de base de datos.

    Returns:
        Lista de objetos Pedido en estado 'Entregado'.
    """
    pedidos_entregados = (
        db.query(Pedido)
        .filter(Pedido.estado_pedido == EstadoPedidoEnum.Entregado)
        .all()
    )

    if not pedidos_entregados:
        logger.info("No hay pedidos entregados en la base de datos.")
        return []

    return pedidos_entregados
