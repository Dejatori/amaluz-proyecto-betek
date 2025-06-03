from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.db.dialect_utils import get_compatible_foreign_key_options


class HistorialDescuento(Base):
    """
    Modelo SQLAlchemy para la tabla de historial de descuentos.
    Representa el historial de descuentos aplicados a los usuarios.
    """
    __tablename__ = "historial_descuentos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id",
                                            **get_compatible_foreign_key_options(ondelete="CASCADE",
                                                                                    onupdate="CASCADE")), nullable=False)
    descuento_id = Column(Integer, ForeignKey("descuentos.id",
                                                **get_compatible_foreign_key_options(ondelete="CASCADE",
                                                                                    onupdate="CASCADE")), nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    usuario = relationship("Usuario")
    descuento = relationship("Descuento", back_populates="historiales")
