import enum
from sqlalchemy import Column, Integer, String, DECIMAL, Enum as SQLAlchemyEnum, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.db.dialect_utils import get_compatible_foreign_key_options


class EstadoEnvioEnum(str, enum.Enum):
    """
    Enumeración para los posibles estados de un envío.
    """
    Pendiente = "Pendiente"
    En_transito = "En tránsito"
    Entregado = "Entregado"
    Devuelto = "Devuelto"
    Incidencia = "Incidencia"


class Envio(Base):
    """
    Modelo SQLAlchemy para la tabla de envíos.
    Representa los envíos de los pedidos a los clientes.
    """
    __tablename__ = "envios"
    __table_args__ = (
        Index("idx_envios_numero_guia", "numero_guia"),
        Index("idx_envios_estado", "estado_envio"),
    )

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id",
                                           **get_compatible_foreign_key_options(ondelete="CASCADE",
                                                                                onupdate="CASCADE")),
                       nullable=False, unique=True)
    empresa_envio = Column(String(100), nullable=False)
    numero_guia = Column(String(50), nullable=False, unique=True)
    costo_envio = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    fecha_envio = Column(DateTime, nullable=True)
    fecha_entrega_estimada = Column(DateTime, nullable=True)
    fecha_entrega_real = Column(DateTime, nullable=True)
    estado_envio = Column(SQLAlchemyEnum(EstadoEnvioEnum,
                                         native_enum=False,
                                         values_callable=lambda x: [e.value for e in x],
                                         ), default=EstadoEnvioEnum.Pendiente)
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    pedido = relationship("Pedido", back_populates="envio")
