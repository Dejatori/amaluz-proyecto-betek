from sqlalchemy import Column, Integer, DECIMAL, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.producto import EstadoProductoEnum
from app.db.dialect_utils import get_compatible_foreign_key_options


class AuditoriaProducto(Base):
    """
    Modelo SQLAlchemy para la tabla de auditoría de productos.
    Registra cambios en el precio y estado de los productos.
    """
    __tablename__ = "auditoria_productos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("productos.id",
                                             **get_compatible_foreign_key_options(ondelete="CASCADE",
                                                                                  onupdate="CASCADE")), nullable=False)
    precio_anterior = Column(DECIMAL(10, 2), nullable=False)
    precio_nuevo = Column(DECIMAL(10, 2), nullable=False)
    estado_anterior = Column(SQLAlchemyEnum(EstadoProductoEnum), default=EstadoProductoEnum.Activo)
    estado_nuevo = Column(SQLAlchemyEnum(EstadoProductoEnum), default=EstadoProductoEnum.Activo)
    fecha_cambio = Column(DateTime, server_default=func.now(), nullable=False)

    # Relación con la tabla de productos
    producto = relationship("Producto")

    def __repr__(self):
        return f"<AuditoriaProducto(id={self.id}, producto_id={self.producto_id}, fecha_cambio='{self.fecha_cambio}')>"
