"""
Módulo para generación de datos de prueba relacionados con el carrito de compras.
Contiene funciones para crear ítems de carrito en la base de datos.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.models.producto import Producto
from app.models.carrito import Carrito

# Configuración
logger = logging.getLogger(__name__)

# Constantes globales para límites temporales
SIMULATION_START_DATE = datetime(2022, 1, 15, 0, 0, 0)
SIMULATION_END_DATE = datetime(2025, 5, 10, 23, 59, 59)


def create_carrito(
        db: Session, usuarios: list[Usuario], productos: list[Producto]
) -> list[Carrito]:
    """
    Crea registros de carrito en la base de datos garantizando al menos una sesión de compra por cliente.
    Prioriza la creación de sesiones sobre las restricciones temporales o de inventario.

    Args:
        db: Sesión de base de datos.
        usuarios: Lista de clientes activos.
        productos: Lista de productos disponibles.

    Returns:
        Lista de objetos Carrito creados.
    """
    carritos_creados = []
    if not usuarios or not productos:
        logger.info("No hay usuarios activos o productos disponibles. No se crearán carritos.")
        return []

    # Ordenar productos y clientes por fecha de registro
    productos_ordenados = sorted(productos, key=lambda p: p.fecha_registro)
    num_productos = len(productos_ordenados)

    clientes_ordenados = sorted(usuarios, key=lambda u: u.fecha_registro)
    num_clientes = len(clientes_ordenados)

    # Productos por sesión
    productos_por_sesion_min = 2
    productos_por_sesion_max = 5

    logger.info(
        f"Generando al menos {num_clientes} sesiones de compra con {productos_por_sesion_min}-{productos_por_sesion_max} "
        f"productos cada una. Productos disponibles: {num_productos}, Clientes: {num_clientes}."
    )

    # Consultar combinaciones ya existentes y productos por cliente
    combinaciones_existentes = set()
    productos_por_cliente = {}

    for item in db.query(Carrito.usuario_id, Carrito.producto_id).all():
        combinaciones_existentes.add((item.usuario_id, item.producto_id))
        if item.usuario_id not in productos_por_cliente:
            productos_por_cliente[item.usuario_id] = set()
        productos_por_cliente[item.usuario_id].add(item.producto_id)

    # Contadores para seguimiento
    clientes_procesados = 0
    clientes_con_sesiones = 0
    total_productos_en_carritos = 0

    # Fecha límite global
    fecha_limite = min(SIMULATION_END_DATE, datetime.now())

    # Procesamos cada cliente
    for cliente in clientes_ordenados:
        clientes_procesados += 1
        cliente_id = cliente.id

        # Verificar si este cliente ya tiene productos en el carrito
        if cliente_id in productos_por_cliente and len(productos_por_cliente[cliente_id]) >= productos_por_sesion_min:
            clientes_con_sesiones += 1
            continue  # Este cliente ya tiene una sesión completa

        # Fecha base para este cliente
        fecha_base_cliente = max(
            SIMULATION_START_DATE,
            cliente.fecha_registro + timedelta(hours=1)  # Al menos 1 hora después de registro
        )

        if fecha_base_cliente >= fecha_limite:
            # Ajustar la fecha para que esté dentro del límite
            fecha_base_cliente = max(
                cliente.fecha_registro + timedelta(hours=1),
                fecha_limite - timedelta(days=30)  # 30 días antes del límite
            )

            if fecha_base_cliente >= fecha_limite:
                # Si aún está fuera de rango, usamos la fecha de registro del cliente
                fecha_base_cliente = cliente.fecha_registro + timedelta(hours=1)

        # Filtrar productos que el cliente pueda comprar (registrados antes de la fecha base)
        productos_disponibles = [
            p for p in productos_ordenados
            if p.fecha_registro < fecha_base_cliente
        ]

        # Si no hay productos disponibles por fecha, intentamos ser más flexibles
        if not productos_disponibles:
            # Usamos todos los productos como fallback
            productos_disponibles = productos_ordenados
            # Ajustamos la fecha base para que sea posterior a todos los productos
            if productos_ordenados:
                fecha_base_cliente = max(
                    fecha_base_cliente,
                    max(p.fecha_registro for p in productos_ordenados) + timedelta(days=1)
                )

        # Filtrar productos que el cliente no tenga ya en el carrito
        productos_no_en_carrito = [
            p for p in productos_disponibles
            if (cliente_id, p.id) not in combinaciones_existentes
        ]

        # Si no hay suficientes productos no en carrito, usamos cualquier producto
        if len(productos_no_en_carrito) < productos_por_sesion_min:
            productos_no_en_carrito = productos_disponibles

        # Verificar si hay productos para este cliente
        if not productos_no_en_carrito:
            logger.warning(f"Cliente {cliente_id}: No hay productos disponibles después de filtrar")
            continue

        # Número de productos para esta sesión
        num_productos_sesion = min(
            random.randint(productos_por_sesion_min, productos_por_sesion_max),
            len(productos_no_en_carrito)
        )

        # Si hay menos productos disponibles que el mínimo, usamos todos
        if num_productos_sesion < productos_por_sesion_min and productos_no_en_carrito:
            num_productos_sesion = len(productos_no_en_carrito)

        # Verificar que haya al menos 1 producto para la sesión
        if num_productos_sesion < 1:
            logger.warning(f"Cliente {cliente_id}: No se pueden seleccionar productos para la sesión")
            continue

        # Seleccionar productos para la sesión (con reemplazos si es necesario)
        productos_seleccionados = []
        productos_ids_usados = set()

        # Intentar seleccionar productos sin repetir
        for _ in range(num_productos_sesion):
            productos_restantes = [p for p in productos_no_en_carrito if p.id not in productos_ids_usados]

            if not productos_restantes:
                # Si ya usamos todos, permitimos repeticiones
                productos_restantes = productos_no_en_carrito

            if productos_restantes:
                producto = random.choice(productos_restantes)
                productos_seleccionados.append(producto)
                productos_ids_usados.add(producto.id)

        # Fecha de la sesión (simulando una sesión de compra)
        fecha_sesion = fecha_base_cliente + timedelta(
            days=random.randint(0, min(30, max(1, (fecha_limite - fecha_base_cliente).days - 1))),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        if fecha_sesion >= fecha_limite:
            fecha_sesion = fecha_base_cliente

        # Variable para controlar si este cliente tuvo éxito
        productos_agregados_en_sesion = 0

        # Añadir productos al carrito en un corto periodo (simulando una sesión)
        for idx, producto in enumerate(productos_seleccionados):
            # Cada producto se añade con pocos minutos de diferencia
            minutos_adicionales = idx * random.randint(1, 3)
            fecha_registro = fecha_sesion + timedelta(minutes=minutos_adicionales)
            fecha_actualizacion = fecha_registro + timedelta(seconds=random.randint(10, 120))

            # SIEMPRE asignar una cantidad entre 1-12 sin verificar inventario
            cantidad_carrito = random.randint(1, 12)

            try:
                # Verificar si ya existe esta combinación
                if (cliente_id, producto.id) in combinaciones_existentes:
                    # Intentar actualizar el carrito existente
                    carrito_existente = db.query(Carrito).filter(
                        Carrito.usuario_id == cliente_id,
                        Carrito.producto_id == producto.id
                    ).first()

                    if carrito_existente:
                        carrito_existente.cantidad = cantidad_carrito
                        carrito_existente.fecha_actualizacion = fecha_actualizacion
                        db.flush()
                        carritos_creados.append(carrito_existente)
                        productos_agregados_en_sesion += 1
                    continue

                # Crear nuevo carrito
                nuevo_carrito = Carrito(
                    usuario_id=cliente_id,
                    producto_id=producto.id,
                    cantidad=cantidad_carrito,
                    fecha_registro=fecha_registro,
                    fecha_actualizacion=fecha_actualizacion
                )

                combinaciones_existentes.add((cliente_id, producto.id))

                # Actualizar el registro de productos por cliente
                if cliente_id not in productos_por_cliente:
                    productos_por_cliente[cliente_id] = set()
                productos_por_cliente[cliente_id].add(producto.id)

                db.add(nuevo_carrito)
                db.flush()

                carritos_creados.append(nuevo_carrito)
                productos_agregados_en_sesion += 1
                total_productos_en_carritos += 1

                if len(carritos_creados) % 100 == 0:
                    db.commit()
                    logger.info(f"Progreso: {len(carritos_creados)} ítems de carrito creados.")

            except Exception as e:
                db.rollback()
                logger.error(f"Error al crear carrito para usuario {cliente_id} y producto {producto.id}: {e}")

        # Si este cliente tuvo al menos un producto agregado, consideramos que tiene sesión
        if productos_agregados_en_sesion > 0:
            clientes_con_sesiones += 1

        # Log de progreso
        if clientes_procesados % 50 == 0 or clientes_procesados == num_clientes:
            logger.info(f"Procesados {clientes_procesados}/{num_clientes} clientes. "
                        f"Clientes con sesiones: {clientes_con_sesiones}. "
                        f"Total productos en carritos: {total_productos_en_carritos}")

    # Commit final
    if carritos_creados:
        try:
            db.commit()
            logger.info(f"Se han creado {len(carritos_creados)} ítems de carrito en total.")
            logger.info(f"{clientes_con_sesiones}/{num_clientes} clientes tienen al menos una sesión de carrito.")
        except Exception as e:
            db.rollback()
            logger.error(f"Error al hacer commit final de carritos: {e}")

    return carritos_creados


def get_carritos(db: Session) -> list[Any] | list[type[Carrito]]:
    """
    Obtiene todos los registros de carrito de la base de datos.

    Args:
        db: Sesión de base de datos.

    Returns:
        Lista de objetos Carrito.
    """
    try:
        carritos = db.query(Carrito).all()
        logger.info(f"Total de carritos obtenidos: {len(carritos)}.")
        return carritos
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener carritos: {e}")
        return []
    except Exception as e:
        logger.error(f"Error inesperado al obtener carritos: {e}")
        return []
