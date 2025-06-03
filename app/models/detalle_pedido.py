from sqlalchemy import Column, Integer, DECIMAL, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.db.dialect_utils import get_compatible_foreign_key_options


class DetallePedido(Base):
    __tablename__ = "detalle_pedido"
    __table_args__ = (
        Index("idx_detalle_pedido_pedido_id", "pedido_id"),
        Index("idx_detalle_pedido_producto_id", "producto_id"),
        UniqueConstraint("pedido_id", "producto_id", name="uq_pedido_producto"),
    )

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id",
                                           **get_compatible_foreign_key_options(ondelete="CASCADE",
                                                                                onupdate="CASCADE")), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id",
                                             **get_compatible_foreign_key_options(ondelete="RESTRICT",
                                                                                  onupdate="CASCADE")), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(DECIMAL(10, 2), nullable=False)
    subtotal = Column(DECIMAL(10, 2), nullable=False)  # Calculado por trigger o en lógica de servicio
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    pedido = relationship("Pedido", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_pedido")
