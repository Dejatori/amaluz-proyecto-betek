from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Proveedor(Base):
    """
    Modelo SQLAlchemy para la tabla de proveedores.
    Representa a los proveedores de productos para la tienda de velas.
    """
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    telefono = Column(String(15), nullable=False)
    direccion = Column(String(255), nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    productos = relationship("Producto", back_populates="proveedor")