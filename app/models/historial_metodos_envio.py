from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.db.dialect_utils import get_compatible_foreign_key_options


class HistorialMetodosEnvio(Base):
    """
    Modelo SQLAlchemy para la tabla de historial de métodos de envío.
    Representa el historial de métodos de envío utilizados por los usuarios.
    """
    __tablename__ = "historial_metodos_envio"
    __table_args__ = (
        CheckConstraint('costo_envio >= 0', name='check_costo_envio_positivo'),
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id",
                                            **get_compatible_foreign_key_options(ondelete="CASCADE",
                                                                                 onupdate="CASCADE")), nullable=False)
    empresa_envio = Column(String(100), nullable=False)
    costo_envio = Column(DECIMAL(10, 2), nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    usuario = relationship("Usuario")