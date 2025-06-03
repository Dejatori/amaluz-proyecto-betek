from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.pedido import EstadoPedidoEnum
from app.db.dialect_utils import get_compatible_foreign_key_options


class AuditoriaPedido(Base):
    """
    Modelo SQLAlchemy para la tabla de auditoría de pedidos.
    Registra cambios en el estado de los pedidos.
    """
    __tablename__ = "auditoria_pedidos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id",
                                           **get_compatible_foreign_key_options(ondelete="CASCADE", onupdate="CASCADE")
                                           ), nullable=False)
    estado_anterior = Column(SQLAlchemyEnum(EstadoPedidoEnum), nullable=False)
    estado_nuevo = Column(SQLAlchemyEnum(EstadoPedidoEnum), nullable=False)
    fecha_cambio = Column(DateTime, server_default=func.now(), nullable=False)

    # Relación con la tabla de pedidos
    pedido = relationship("Pedido")

    def __repr__(self):
        return f"<AuditoriaPedido(id={self.id}, pedido_id={self.pedido_id}, fecha_cambio='{self.fecha_cambio}')>"
