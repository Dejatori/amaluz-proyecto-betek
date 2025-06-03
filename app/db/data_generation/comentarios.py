"""
Módulo para generación de datos de prueba relacionados con comentarios de productos.
Contiene funciones para crear comentarios en la base de datos.
"""

import random
import logging
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy.orm import Session

from app.core.ai_generators import generate_comentario_ia
from app.models import Comentario, Pedido, Usuario, Producto
from app.db.data_generation.utils_datetime import (
    SIMULATION_END_DATE,
)

# Configuración
logger = logging.getLogger(__name__)
fake = Faker("es_CO")


def create_comentario(
    db: Session,
    pedido: Pedido,
    fecha_entrega: datetime,
    porcentaje_comentario: float,
    min_days_post_entrega: int,
    max_days_post_entrega: int,
):
    """
    Genera comentarios para los productos de un pedido entregado, con probabilidad dada.
    Args:
        db: Sesión de base de datos.
        pedido: Objeto Pedido ya entregado.
        fecha_entrega: Fecha en que el pedido fue entregado.
        porcentaje_comentario: Probabilidad de que se genere comentario por producto.
        min_days_post_entrega: Días mínimos después de la entrega para el comentario.
        max_days_post_entrega: Días máximos después de la entrega para el comentario.
    """
    if not pedido.detalles:
        logger.debug(f"Pedido {pedido.id} no tiene detalles para comentarios.")
        return

    usuario_obj = db.query(Usuario).get(pedido.usuario_id)
    if not usuario_obj:
        logger.debug(
            f"Usuario {pedido.usuario_id} no encontrado para pedido {pedido.id}."
        )
        return

    for detalle in pedido.detalles:
        producto_obj = db.query(Producto).get(detalle.producto_id)
        if not producto_obj:
            continue

        if random.random() > porcentaje_comentario:
            continue

        # Calcular fecha coherente para el comentario
        min_fecha = max(
            fecha_entrega, usuario_obj.fecha_registro, producto_obj.fecha_registro
        )
        if min_fecha >= SIMULATION_END_DATE:
            fecha_registro_comentario = SIMULATION_END_DATE
        else:
            offset_dias = timedelta(
                days=random.randint(min_days_post_entrega, max_days_post_entrega)
            )
            offset_segundos = timedelta(seconds=random.randint(0, (24 * 60 * 60) - 1))
            fecha_registro_comentario = min(
                min_fecha + offset_dias + offset_segundos, SIMULATION_END_DATE
            )
            if fecha_registro_comentario < min_fecha:
                fecha_registro_comentario = min_fecha

        if fecha_registro_comentario > SIMULATION_END_DATE:
            continue

        # Fecha de actualización del comentario
        fecha_actualizacion_comentario = fecha_registro_comentario + timedelta(
            seconds=random.randint(0, 3600)
        )
        if fecha_actualizacion_comentario < fecha_registro_comentario:
            fecha_actualizacion_comentario = fecha_registro_comentario
        if fecha_actualizacion_comentario > SIMULATION_END_DATE:
            fecha_actualizacion_comentario = SIMULATION_END_DATE

        calificacion = random.randint(1, 5)

        context= (
            f"Eres un usuario que ha comprado el producto con las siguientes características: "
            f"Producto: {producto_obj.nombre}, "
            f"Descripción: {producto_obj.descripcion}, "
            f"Categoría: {producto_obj.categoria}, "
            f"Calificación: {calificacion}. "

        )

        comentario_texto = generate_comentario_ia(context) #  Comentario generado por IA

        nuevo_comentario = Comentario(
            usuario_id=usuario_obj.id,
            producto_id=producto_obj.id,
            comentario= comentario_texto,
            calificacion=calificacion,
            fecha_registro=fecha_registro_comentario,
            fecha_actualizacion=fecha_actualizacion_comentario,
        )
        db.add(nuevo_comentario)
        logger.info(
            f"Comentario simulado para producto {producto_obj.id} del pedido {pedido.id}"
        )

    db.flush()
