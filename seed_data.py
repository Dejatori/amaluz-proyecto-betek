"""
Script para poblar la base de datos.
Ejecución:
    python seed_data.py
"""
import logging
import random

from app.core.logging import configure_logging

from sqlalchemy.exc import IntegrityError

from app.db.database import get_sync_db
from app.db.data_generation.usuarios import (
    create_users,
    update_user_estado,
    get_usuarios_activos_clientes,
)
from app.db.data_generation.proveedores import create_proveedores
from app.db.data_generation.productos import create_productos, get_productos
from app.db.data_generation.inventario import create_inventario_inicial
from app.db.data_generation.pedidos import create_pedidos
from app.db.data_generation.descuentos import create_descuentos, get_descuentos
from app.db.data_generation.carrito import create_carrito, get_carritos

# Configuración de logging
configure_logging()
logging.getLogger("app.core.security").setLevel(logging.INFO)
logger = logging.getLogger(__name__)


# --- Constantes de generación ---
USUARIOS_COUNT = 50
PROVEEDORES_COUNT = 10
PRODUCTOS_COUNT = 20

# Volumen de pedidos
PEDIDOS_COUNT = 10


# --- Orquestador principal ---
def main():
    with get_sync_db() as db:
        try:
            logger.info("Iniciando la creación de datos de prueba...")

            logger.info("Creando usuarios...")
            usuarios = create_users(db, USUARIOS_COUNT)
            logger.info(f"Creados {len(usuarios)} usuarios.")

            logger.info("Iniciando actualización de estado de usuarios 'Sin confirmar'...")
            update_user_estado(db, random.randint(int(USUARIOS_COUNT * 0.05), int(USUARIOS_COUNT * 0.10)))
            logger.info("Estado de usuarios 'Sin confirmar' actualizado.")

            logger.info("Obtención de clientes activos...")
            usuarios_activos_clientes = get_usuarios_activos_clientes(db)
            logger.info(f"Total de clientes activos: {len(usuarios_activos_clientes)}.")

            logger.info("Creando proveedores...")
            proveedores = create_proveedores(db, PROVEEDORES_COUNT)
            logger.info(f"Creados {len(proveedores)} proveedores.")

            logger.info("Creando productos...")
            productos = create_productos(db, PRODUCTOS_COUNT, proveedores)
            logger.info(f"Creados {len(productos)} productos.")

            logger.info("Creando inventario inicial...")
            inventarios = create_inventario_inicial(db, productos)
            logger.info(f"Creados {len(inventarios)} registros de inventario.")

            logger.info("Creando descuentos...")
            descuentos = create_descuentos(db)
            logger.info(f"Creados {len(descuentos)} descuentos.")

            logger.info("Creando carritos...")
            carritos = create_carrito(db, usuarios_activos_clientes, productos)
            logger.info(f"Creados {len(carritos)} ítems de carrito.")

            logger.info("Creando pedidos...")
            pedidos_pendientes = create_pedidos(db, descuentos, carritos)
            logger.info(f"Creados {len(pedidos_pendientes)} pedidos.")

            logger.info("¡Datos de prueba generados exitosamente!")

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error de integridad durante la inserción de datos: {e}")
            logger.error("Detalles del error original:", exc_info=True)
        except Exception as e:
            db.rollback()
            logger.error(f"Error inesperado durante la generación de datos: {e}")
            logger.error("Detalles del error:", exc_info=True)


if __name__ == "__main__":
    main()
