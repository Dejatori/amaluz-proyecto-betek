from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.db.dialect_utils import get_compatible_foreign_key_options


class LocalizacionPedido(Base):
    """
    Modelo SQLAlchemy para la tabla de localización de pedido (direcciones).
    Representa las direcciones de entrega para los pedidos.
    """
    __tablename__ = "localizacion_pedido"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id",
                                            **get_compatible_foreign_key_options(ondelete="CASCADE",
                                                                                 onupdate="CASCADE")), nullable=False)
    direccion_1 = Column(String(255), nullable=False)
    direccion_2 = Column(String(255), nullable=True)
    ciudad = Column(String(100), nullable=False)
    departamento = Column(String(100), nullable=False)
    codigo_postal = Column(String(10), nullable=False)
    descripcion = Column(Text, nullable=True)
    notas_entrega = Column(Text, nullable=True)
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="localizaciones")
    pedidos = relationship("Pedido", back_populates="localizacion")