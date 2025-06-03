"""
Módulo para generación de datos de prueba relacionados con el inventario.
Contiene funciones para crear registros de inventario inicial para productos.
"""

import random
import logging
from decimal import Decimal
from typing import Tuple, Optional
from collections import defaultdict

from faker import Faker
from datetime import timedelta, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.data_generation.utils_datetime import get_random_datetime_in_range
from app.models import Pedido, Comentario, Carrito
from app.models.detalle_pedido import DetallePedido
from app.models.pedido import EstadoPedidoEnum
from app.models.producto import Producto, EstadoProductoEnum
from app.models.inventario import Inventario

# Configuración
logger = logging.getLogger(__name__)
fkr = Faker("es_CO")

# --- Constantes de Fechas ---
PRODUCTOS_END_DATE_LIMIT = datetime(2025, 5, 15, 10, 0, 0)
MIN_SECONDS_AFTER_PREVIOUS_UPDATE = 1

# --- Constantes de Inventario ---
UMBRAL_REPOSICION = 12  # Productos a partir de los cuales se considera reponer
PERIODO_MINIMO_REPOSICION = 20  # Días mínimos entre reposiciones del mismo producto

# Diccionario que registra las ventas históricas por producto
VENTAS_POR_PRODUCTO = defaultdict(int)

# Diccionario para controlar la fecha de última reposición de cada producto
ultimas_reposiciones = {}


def determinar_cantidad_reposicion(nivel_popularidad, ranking_en_categoria):
    """
    Determina la cantidad de reposición según la popularidad y el ranking del producto.

    Args:
        nivel_popularidad: Nivel de popularidad del producto (0-10)
        ranking_en_categoria: Posición del producto dentro de su categoría de popularidad

    Returns:
        Cantidad de unidades a reponer
    """
    # Productos populares (8-10)
    if nivel_popularidad >= 8:
        if ranking_en_categoria == 1:  # El más popular
            return 108
        elif ranking_en_categoria <= 4:  # Los siguientes 3 más populares
            return 96
        else:  # Resto de productos populares
            return 84

    # Productos medios (4-7)
    elif nivel_popularidad >= 4:
        if ranking_en_categoria == 1:  # El más popular de los medios
            return 72
        elif ranking_en_categoria <= 3:  # Los siguientes 2 más populares medios
            return 64
        else:  # Resto de productos medios
            return 48

    # Productos poco populares (0-3)
    else:
        if ranking_en_categoria == 1:  # El más "popular" de los poco populares
            return 36
        elif ranking_en_categoria <= 3:  # Los siguientes 2 menos impopulares
            return 24
        else:  # Los productos realmente poco populares
            return 12


def calcular_cantidad_reposicion(db, producto_id):
    """
    Calcula la cantidad a reponer de un producto específico basado en su popularidad.

    Args:
        db: Sesión de base de datos
        producto_id: ID del producto a reponer

    Returns:
        Cantidad de unidades a reponer
    """
    # Calcular popularidad de todos los productos
    productos = (
        db.query(Producto).filter(Producto.estado == EstadoProductoEnum.Activo).all()
    )

    # Calcular popularidad para cada producto
    productos_con_popularidad = []
    for producto in productos:
        nivel_popularidad = calcular_popularidad(db, producto.id)
        productos_con_popularidad.append((producto, nivel_popularidad))

    # Agrupar productos por nivel de popularidad
    productos_populares = []
    productos_medios = []
    productos_poco_populares = []

    for producto, popularidad in productos_con_popularidad:
        if popularidad >= 8:
            productos_populares.append((producto, popularidad))
        elif popularidad >= 4:
            productos_medios.append((producto, popularidad))
        else:
            productos_poco_populares.append((producto, popularidad))

    # Ordenar cada grupo por popularidad (descendente)
    productos_populares.sort(key=lambda x: x[1], reverse=True)
    productos_medios.sort(key=lambda x: x[1], reverse=True)
    productos_poco_populares.sort(key=lambda x: x[1], reverse=True)

    # Determinar el nivel de popularidad y el ranking del producto actual
    nivel_popularidad = 0
    ranking_en_categoria = 1

    # Buscar el producto en los grupos y determinar su ranking
    producto_encontrado = False

    # Buscar en productos populares
    for idx, (producto, popularidad) in enumerate(productos_populares):
        if producto.id == producto_id:
            nivel_popularidad = popularidad
            ranking_en_categoria = idx + 1
            producto_encontrado = True
            break

    # Buscar en productos medios
    if not producto_encontrado:
        for idx, (producto, popularidad) in enumerate(productos_medios):
            if producto.id == producto_id:
                nivel_popularidad = popularidad
                ranking_en_categoria = idx + 1
                producto_encontrado = True
                break

    # Buscar en productos poco populares
    if not producto_encontrado:
        for idx, (producto, popularidad) in enumerate(productos_poco_populares):
            if producto.id == producto_id:
                nivel_popularidad = popularidad
                ranking_en_categoria = idx + 1
                producto_encontrado = True
                break

    # Si por algún motivo no se encontró el producto, asignar valores por defecto
    if not producto_encontrado:
        logger.warning(
            f"Producto ID {producto_id} no encontrado en ninguna categoría de popularidad"
        )
        return 24  # Valor mínimo de reposición por defecto

    # Determinar cantidad de reposición según popularidad y ranking
    return determinar_cantidad_reposicion(nivel_popularidad, ranking_en_categoria)


def calcular_popularidad(db, producto_id):
    """
    Calcula el nivel de popularidad de un producto (0-10) basado en:
    - Cantidad de ventas
    - Comentarios positivos
    - Inclusión en carritos

    Args:
        db: Sesión de base de datos
        producto_id: ID del producto

    Returns:
        Nivel de popularidad en escala 0-10
    """
    # Contar ventas (detalles de pedido de pedidos entregados)
    ventas = (
        db.query(func.sum(DetallePedido.cantidad))
        .join(Pedido)
        .filter(DetallePedido.producto_id == producto_id)
        .filter(
            Pedido.estado_pedido.in_(
                [EstadoPedidoEnum.Entregado, EstadoPedidoEnum.Enviado]
            )
        )
        .scalar()
        or 0
    )

    # Contar comentarios positivos (calificación >= 4)
    comentarios_positivos = (
        db.query(func.count(Comentario.id))
        .filter(Comentario.producto_id == producto_id)
        .filter(Comentario.calificacion >= 4)
        .scalar()
        or 0
    )

    # Contar inclusiones en carritos
    en_carritos = (
        db.query(func.sum(Carrito.cantidad))
        .filter(Carrito.producto_id == producto_id)
        .scalar()
        or 0
    )

    # Normalizar y combinar factores para obtener popularidad en escala 0-10
    # Estos pesos son ajustables según la importancia relativa de cada factor
    peso_ventas = 0.6
    peso_comentarios = 0.3
    peso_carritos = 0.1

    # Obtener máximos para normalización
    max_ventas = (
        db.query(func.sum(DetallePedido.cantidad))
        .join(Pedido)
        .filter(
            Pedido.estado_pedido.in_(
                [EstadoPedidoEnum.Entregado, EstadoPedidoEnum.Enviado]
            )
        )
        .group_by(DetallePedido.producto_id)
        .order_by(func.sum(DetallePedido.cantidad).desc())
        .first()
    )

    max_comentarios = (
        db.query(func.count(Comentario.id))
        .filter(Comentario.calificacion >= 4)
        .group_by(Comentario.producto_id)
        .order_by(func.count(Comentario.id).desc())
        .first()
    )

    max_carritos = (
        db.query(func.sum(Carrito.cantidad))
        .group_by(Carrito.producto_id)
        .order_by(func.sum(Carrito.cantidad).desc())
        .first()
    )

    # Evitar división por cero
    max_ventas = max_ventas[0] if max_ventas else 1
    max_comentarios = max_comentarios[0] if max_comentarios else 1
    max_carritos = max_carritos[0] if max_carritos else 1

    # Calcular puntuación normalizada
    puntuacion_ventas = (ventas / max_ventas) * 10 if max_ventas > 0 else 0
    puntuacion_comentarios = (
        (comentarios_positivos / max_comentarios) * 10 if max_comentarios > 0 else 0
    )
    puntuacion_carritos = (en_carritos / max_carritos) * 10 if max_carritos > 0 else 0

    # Convierte los pesos a Decimal antes de multiplicar
    puntuacion_ventas = Decimal(str(puntuacion_ventas))
    puntuacion_comentarios = Decimal(str(puntuacion_comentarios))
    puntuacion_carritos = Decimal(str(puntuacion_carritos))
    peso_carritos = Decimal(str(peso_carritos))
    peso_ventas = Decimal(str(peso_ventas))
    peso_comentarios = Decimal(str(peso_comentarios))

    # Calcular popularidad ponderada
    popularidad = (
        puntuacion_ventas * peso_ventas
        + puntuacion_comentarios * peso_comentarios
        + puntuacion_carritos * peso_carritos
    )

    # Asegurar que esté en el rango 0-10
    return min(10, max(0, popularidad))


def create_inventario_inicial(
    db: Session, productos: list[Producto]
) -> list[Inventario]:
    """
    Crea registros de inventario inicial para la lista de productos proporcionada.
    La fecha_registro del inventario será >= producto.fecha_registro.
    La fecha_actualizacion del inventario será == inventario.fecha_registro.

    Args:
        db: Sesión de base de datos.
        productos: Lista de objetos Producto para los cuales crear inventario.

    Returns:
        Lista de objetos Inventario creados.
    """
    inventarios_creados = []

    if not productos:
        logger.warning(
            "No se proporcionaron productos. No se puede crear inventario inicial."
        )
        return []

    for producto in productos:
        # Cota inferior para la fecha de registro del inventario es la fecha de registro del producto.
        cota_inferior_fecha_reg_inv = producto.fecha_registro

        # Cota superior: unos segundos después del registro del producto
        cota_superior_fecha_reg_inv = min(
            producto.fecha_registro + timedelta(seconds=random.randint(10, 300)),
            PRODUCTOS_END_DATE_LIMIT,
        )

        # Asegurar que la cota inferior no sea mayor que la superior
        if cota_inferior_fecha_reg_inv > cota_superior_fecha_reg_inv:
            # Esto podría pasar si producto.fecha_registro está muy cerca de PRODUCTOS_END_DATE_LIMIT
            fecha_registro_inv = cota_inferior_fecha_reg_inv
        else:
            fecha_registro_inv = get_random_datetime_in_range(
                cota_inferior_fecha_reg_inv, cota_superior_fecha_reg_inv
            )

        cantidad_inicial = 24

        nuevo_inventario = Inventario(
            producto_id=producto.id,
            cantidad_mano=cantidad_inicial,
            cantidad_disponible=cantidad_inicial,
            fecha_registro=fecha_registro_inv,
            fecha_actualizacion=fecha_registro_inv,  # Establecer igual a fecha_registro para la creación inicial
        )
        inventarios_creados.append(nuevo_inventario)

    if inventarios_creados:
        try:
            db.add_all(inventarios_creados)
            db.commit()
            for inv in inventarios_creados:
                db.refresh(inv)  # Refrescar para obtener IDs y estados de la BD
            logger.info(
                f"Creados {len(inventarios_creados)} registros de inventario inicial."
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error al crear inventario inicial: {e}", exc_info=True)
    else:
        logger.info(
            "No se crearon registros de inventario inicial (o no hubo productos válidos)."
        )

    return inventarios_creados


def actualizar_inventario_por_pedido(
    db: Session, detalle_pedido: DetallePedido, fecha_operacion: datetime
) -> Tuple[bool, Optional[Inventario]]:
    """
    Actualiza el inventario cuando se crea un detalle de pedido.

    Args:
        db: Sesión de base de datos.
        detalle_pedido: Detalle del pedido que afecta al inventario.
        fecha_operacion: Fecha en que se realiza la operación (debe ser coherente con el detalle).

    Returns:
        Tupla (éxito, inventario_actualizado)
    """
    try:
        # Obtener el inventario asociado al producto del detalle
        inventario = (
            db.query(Inventario)
            .filter(Inventario.producto_id == detalle_pedido.producto_id)
            .first()
        )

        if not inventario:
            logger.warning(
                f"No existe inventario para el producto {detalle_pedido.producto_id}"
            )
            return False, None

        # Verificar si hay stock suficiente
        cantidad_solicitada = detalle_pedido.cantidad
        if inventario.cantidad_disponible < cantidad_solicitada:
            logger.warning(
                f"Stock insuficiente para producto {detalle_pedido.producto_id}. "
                f"Solicitado: {cantidad_solicitada}, Disponible: {inventario.cantidad_disponible}"
            )
            return False, inventario

        # Decrementar inventario
        inventario.cantidad_disponible -= cantidad_solicitada
        inventario.cantidad_mano -= cantidad_solicitada
        inventario.fecha_actualizacion = fecha_operacion

        # Si el producto queda sin stock, marcar como inactivo
        if inventario.cantidad_disponible == 0:
            producto = db.query(Producto).get(detalle_pedido.producto_id)
            if producto and producto.estado != EstadoProductoEnum.Inactivo:
                producto.estado = EstadoProductoEnum.Inactivo
                producto.fecha_actualizacion = fecha_operacion
                logger.info(
                    f"Producto {producto.id} marcado como Inactivo por agotamiento de stock"
                )

        db.flush()  # Persistir cambios pero sin commit aún

        # Verificar si se requiere reposición
        reponer = verificar_reposicion_inventario(db, inventario, fecha_operacion)
        if reponer:
            logger.info(
                f"Se programó reposición para producto {inventario.producto_id}"
            )

        return True, inventario

    except SQLAlchemyError as e:
        logger.error(f"Error al actualizar inventario: {e}")
        db.rollback()
        return False, None


def verificar_reposicion_inventario(
    db: Session, inventario: Inventario, fecha_operacion: datetime
) -> bool:
    """
    Verifica si se debe reponer el inventario y lo hace si es necesario.
    La fecha de actualización del inventario para la reposición será la fecha_reposicion calculada.

    Args:
        db: Sesión de base de datos.
        inventario: Registro de inventario a verificar.
        fecha_operacion: Fecha de la operación actual que podría disparar la reposición.

    Returns:
        True si se realizó reposición, False en caso contrario.
    """
    producto_id = inventario.producto_id

    if inventario.cantidad_disponible < UMBRAL_REPOSICION:
        ultima_reposicion = ultimas_reposiciones.get(producto_id)

        if ultima_reposicion:
            fecha_minima_reposicion = ultima_reposicion + timedelta(
                days=PERIODO_MINIMO_REPOSICION
            )
            if fecha_operacion < fecha_minima_reposicion:
                logger.debug(
                    f"No se puede reponer producto {producto_id} hasta {fecha_minima_reposicion}. "
                    f"Última reposición: {ultima_reposicion}."
                )
                return False

        cantidad_repuesta = calcular_cantidad_reposicion(db, producto_id)

        dias_reposicion = random.randint(1, 5)
        fecha_reposicion_calculada = fecha_operacion + timedelta(days=dias_reposicion)

        if fecha_reposicion_calculada > PRODUCTOS_END_DATE_LIMIT:
            fecha_reposicion_calculada = PRODUCTOS_END_DATE_LIMIT

        # Guardar la fecha de actualización actual del inventario antes de modificarla
        fecha_actualizacion_inventario_previa = inventario.fecha_actualizacion

        inventario.cantidad_disponible += cantidad_repuesta
        inventario.cantidad_mano += cantidad_repuesta

        # Establecer la fecha_actualizacion del inventario a la fecha_reposicion_calculada,
        # asegurando que el tiempo avance.
        if fecha_reposicion_calculada <= fecha_actualizacion_inventario_previa:
            inventario.fecha_actualizacion = fecha_actualizacion_inventario_previa + timedelta(
                seconds=MIN_SECONDS_AFTER_PREVIOUS_UPDATE
            )
        else:
            inventario.fecha_actualizacion = fecha_reposicion_calculada

        ultimas_reposiciones[producto_id] = inventario.fecha_actualizacion # Usar la fecha que realmente se asignó

        producto = db.query(Producto).get(producto_id)
        if producto and producto.estado == EstadoProductoEnum.Inactivo:
            # Guardar la fecha de actualización actual del producto antes de modificarla
            fecha_actualizacion_producto_previa = producto.fecha_actualizacion

            producto.estado = EstadoProductoEnum.Activo

            # La fecha de actualización del producto debe ser coherente con la fecha de reposición del inventario.
            fecha_reactivacion_producto = inventario.fecha_actualizacion

            if fecha_reactivacion_producto <= fecha_actualizacion_producto_previa:
                producto.fecha_actualizacion = (
                        fecha_actualizacion_producto_previa
                        + timedelta(seconds=MIN_SECONDS_AFTER_PREVIOUS_UPDATE)
                )
            else:
                producto.fecha_actualizacion = fecha_reactivacion_producto

            logger.info(
                f"Producto {producto_id} reactivado con stock {inventario.cantidad_disponible} "
                f"en {producto.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        logger.info(
            f"Reposición de {cantidad_repuesta} unidades para producto {producto_id} "
            f"programada para {inventario.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return True

    return False


def validar_disponibilidad_producto(
    db: Session, producto_id: int, cantidad_requerida: int
) -> bool:
    """
    Valida si hay suficiente inventario disponible para un producto.

    Args:
        db: Sesión de base de datos.
        producto_id: ID del producto a verificar.
        cantidad_requerida: Cantidad de producto que se quiere reservar.

    Returns:
        True si hay suficiente inventario, False en caso contrario.
    """
    try:
        # Verificar si el producto existe y está activo
        producto = db.query(Producto).get(producto_id)
        if not producto or producto.estado != EstadoProductoEnum.Activo:
            return False

        # Verificar inventario disponible
        inventario = (
            db.query(Inventario).filter(Inventario.producto_id == producto_id).first()
        )

        if not inventario or inventario.cantidad_disponible < cantidad_requerida:
            return False

        return True

    except SQLAlchemyError as e:
        logger.error(f"Error al validar disponibilidad del producto {producto_id}: {e}")
        return False


def reponer_stock_tras_cancelacion(
    db: Session, producto_id: int, cantidad_repuesta: int, fecha_operacion: datetime
) -> Tuple[bool, Optional[Inventario]]:
    """
    Repone el stock de un producto cuando un detalle de pedido se cancela.
    Incrementa la cantidad disponible y en mano.
    Reactiva el producto si estaba inactivo y ahora tiene stock.

    Args:
        db: Sesión de base de datos.
        producto_id: ID del producto cuyo stock se va a reponer.
        cantidad_repuesta: Cantidad de producto a reponer.
        fecha_operacion: Fecha en que se realiza la operación de reposición.

    Returns:
        Tupla (éxito, inventario_actualizado)
    """
    try:
        inventario = (
            db.query(Inventario)
            .filter(Inventario.producto_id == producto_id)
            .with_for_update()  # Para consistencia si hay concurrencia
            .first()
        )

        if not inventario:
            logger.warning(
                f"No se encontró inventario para el producto {producto_id} al intentar reponer stock por cancelación."
            )
            return False, None

        cantidad_anterior_disponible = inventario.cantidad_disponible
        inventario.cantidad_disponible += cantidad_repuesta
        inventario.cantidad_mano += cantidad_repuesta
        inventario.fecha_actualizacion = fecha_operacion

        # Si el producto estaba inactivo y ahora tiene stock (o tenía 0 y se repone), reactivarlo
        if cantidad_anterior_disponible <= 0 < inventario.cantidad_disponible:
            producto = db.query(Producto).get(producto_id)
            if producto and producto.estado == EstadoProductoEnum.Inactivo:
                producto.estado = EstadoProductoEnum.Activo
                producto.fecha_actualizacion = fecha_operacion
                logger.info(
                    f"Producto {producto_id} reactivado con {inventario.cantidad_disponible} unidades en stock tras cancelación."
                )

        db.flush()  # Persiste los cambios en la sesión, el commit lo hará la función que llama.

        logger.info(
            f"Stock repuesto para producto {producto_id} en {cantidad_repuesta} unidades. "
            f"Disponible: {inventario.cantidad_disponible}, En Mano: {inventario.cantidad_mano}."
        )
        return True, inventario

    except SQLAlchemyError as e:
        logger.error(
            f"Error al reponer stock por cancelación para producto {producto_id}: {e}",
            exc_info=True,
        )
        # El rollback general lo debería manejar la función que llama
        return False, None


def obtener_cantidad_disponible(db: Session, producto_id: int) -> int:
    """
    Obtiene la cantidad disponible de un producto en el inventario.

    Args:
        db: Sesión de base de datos.
        producto_id: ID del producto.

    Returns:
        Cantidad disponible o 0 si no hay inventario.
    """
    try:
        inventario = (
            db.query(Inventario).filter(Inventario.producto_id == producto_id).first()
        )

        return inventario.cantidad_disponible if inventario else 0

    except Exception as e:
        logger.error(
            f"Error al obtener cantidad disponible para producto {producto_id}: {e}"
        )
        return 0
