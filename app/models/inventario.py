from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.db.dialect_utils import get_compatible_foreign_key_options


class Inventario(Base):
    """
    Modelo SQLAlchemy para la tabla de inventario.
    Representa el inventario de productos disponibles en la tienda de velas.
    """
    __tablename__ = "inventario"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id",
                                             **get_compatible_foreign_key_options(ondelete="CASCADE",
                                                                                  onupdate="CASCADE")),
                         nullable=False, unique=True)
    cantidad_mano = Column(Integer, nullable=False, default=0)
    cantidad_disponible = Column(Integer, nullable=False, default=0)
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    producto = relationship("Producto", back_populates="inventario")
