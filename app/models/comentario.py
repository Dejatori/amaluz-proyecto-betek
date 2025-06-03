from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, CheckConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.db.dialect_utils import get_compatible_foreign_key_options


class Comentario(Base):
    """
    Modelo SQLAlchemy para la tabla de comentarios y calificaciones.
    Representa los comentarios y calificaciones de los usuarios sobre los productos.
    """
    __tablename__ = "comentarios"
    __table_args__ = (
        CheckConstraint('calificacion >= 1 AND calificacion <= 5', name='check_calificacion_rango'),
        Index("idx_comentarios_producto_id", "producto_id"),
        Index("idx_comentarios_usuario_id", "usuario_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id",
                                            **get_compatible_foreign_key_options(ondelete="CASCADE",
                                                                                 onupdate="CASCADE")), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id",
                                             **get_compatible_foreign_key_options(ondelete="CASCADE",
                                                                                  onupdate="CASCADE")), nullable=False)
    comentario = Column(Text, nullable=False)
    calificacion = Column(Integer, nullable=True)  # Puede ser NULL si solo es un comentario sin calificación
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="comentarios")
    producto = relationship("Producto", back_populates="comentarios")