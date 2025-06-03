# Importa la clase SQLAlchemy de flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy

# Crea una instancia de SQLAlchemy
db = SQLAlchemy()


def init_db(app):
    """
    Inicializa la base de datos con la aplicación Flask proporcionada.

    Args:
        app (Flask): La instancia de la aplicación Flask.
    """
    db.init_app(app)


# Importa los modelos de la base de datos
from .amaluz import Empleado, Proveedor, Producto, Cliente, Pedido, DetallePedido, Envio, Calificacion, Inventario, \
    AuditoriaInventario

# Define qué elementos se exportan cuando se importa el módulo
__all__ = ['db', 'init_db',
           'Empleado', 'Proveedor', 'Producto', 'Cliente',
           'Pedido', 'DetallePedido', 'Envio', 'Calificacion',
           'Inventario', 'AuditoriaInventario']
