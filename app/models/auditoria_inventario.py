from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.db.dialect_utils import get_compatible_foreign_key_options


class AuditoriaInventario(Base):
    """
    Modelo SQLAlchemy para la tabla de auditoría de inventario.
    Registra cambios en la cantidad de productos en inventario.
    """
    __tablename__ = "auditoria_inventario"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("productos.id",
                                             **get_compatible_foreign_key_options(ondelete="CASCADE", onupdate="CASCADE")
                                             ), nullable=False)
    cantidad_anterior = Column(Integer, nullable=False)
    cantidad_nueva = Column(Integer, nullable=False)
    fecha_cambio = Column(DateTime, server_default=func.now(), nullable=False)

    # Relación con la tabla de productos (ya que el FK es a productos.id)
    producto = relationship("Producto")

    def __repr__(self):
        return f"<AuditoriaInventario(id={self.id}, producto_id={self.producto_id}, fecha_cambio='{self.fecha_cambio}')>"
