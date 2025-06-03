import enum
from sqlalchemy import Column, Integer, String, DECIMAL, Enum as SQLAlchemyEnum, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class EstadoDescuentoEnum(str, enum.Enum):
    """
    Enumeración para los posibles estados de un descuento.
    """
    Activo = "Activo"
    Inactivo = "Inactivo"


class Descuento(Base):
    """
    Modelo SQLAlchemy para la tabla de descuentos.
    Representa los descuentos disponibles para aplicar a los pedidos.
    """
    __tablename__ = "descuentos"
    __table_args__ = (
        CheckConstraint('fecha_fin >= fecha_inicio', name='check_fechas_validas'),
        CheckConstraint('porcentaje > 0 AND porcentaje <= 100', name='check_porcentaje_valido'),
    )

    id = Column(Integer, primary_key=True, index=True)
    codigo_descuento = Column(String(50), nullable=False, unique=True, index=True)
    porcentaje = Column(DECIMAL(5, 2), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    estado = Column(SQLAlchemyEnum(EstadoDescuentoEnum), default=EstadoDescuentoEnum.Activo)
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    historiales = relationship("HistorialDescuento", back_populates="descuento")