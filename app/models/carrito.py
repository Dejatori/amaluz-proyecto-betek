from sqlalchemy import Column, Integer, ForeignKey, DateTime, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.db.dialect_utils import get_compatible_foreign_key_options


class Carrito(Base):
    """
    Modelo SQLAlchemy para la tabla de carrito de compras.
    Representa los productos añadidos al carrito de compras de un usuario.
    """
    __tablename__ = "carrito"
    __table_args__ = (
        CheckConstraint('cantidad > 0', name='check_cantidad_positiva'),
        UniqueConstraint('usuario_id', 'producto_id', name='uq_usuario_producto'),
        Index("idx_carrito_usuario_id", "usuario_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id",
                                            **get_compatible_foreign_key_options(ondelete="CASCADE",
                                                                                 onupdate="CASCADE")), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id",
                                             **get_compatible_foreign_key_options(ondelete="CASCADE",
                                                                                  onupdate="CASCADE")), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="carrito_items")
    producto = relationship("Producto", back_populates="carrito_items")
