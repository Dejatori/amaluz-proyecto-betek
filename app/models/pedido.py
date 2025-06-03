import enum
from sqlalchemy import Column, Integer, String, DECIMAL, Enum as SQLAlchemyEnum, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.db.dialect_utils import get_compatible_foreign_key_options


class MetodoPagoEnum(str, enum.Enum):
    Tarjeta_de_Credito = "Tarjeta de Crédito"
    Transferencia_Bancaria = "Transferencia Bancaria"
    PSE = "PSE"


class EstadoPedidoEnum(str, enum.Enum):
    Pendiente = "Pendiente"
    Procesando = "Procesando"
    Enviado = "Enviado"
    Entregado = "Entregado"
    Cancelado = "Cancelado"
    Reembolsado = "Reembolsado"


class Pedido(Base):
    __tablename__ = "pedidos"
    __table_args__ = (
        Index("idx_pedidos_usuario_id", "usuario_id"),
        Index("idx_pedidos_estado", "estado_pedido"),
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id",
                                            **get_compatible_foreign_key_options(ondelete="RESTRICT",
                                                                                 onupdate="CASCADE")), nullable=False)
    id_localizacion = Column(Integer, ForeignKey("localizacion_pedido.id",
                                            **get_compatible_foreign_key_options(ondelete="RESTRICT",
                                                                                 onupdate="CASCADE")), nullable=False)
    codigo_pedido = Column(String(50), nullable=False, unique=True)
    costo_total = Column(DECIMAL(10, 2), nullable=False)
    metodo_pago = Column(SQLAlchemyEnum(MetodoPagoEnum,
                                        native_enum=False,
                                        values_callable=lambda x: [e.value for e in x],
                                        ), nullable=False)
    estado_pedido = Column(SQLAlchemyEnum(EstadoPedidoEnum), default=EstadoPedidoEnum.Pendiente)
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="pedidos")
    localizacion = relationship("LocalizacionPedido")
    detalles = relationship("DetallePedido", back_populates="pedido", cascade="all, delete-orphan")
    envio = relationship("Envio", back_populates="pedido", uselist=False)  # One-to-one
