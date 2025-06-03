from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.usuario import EstadoUsuarioEnum
from app.db.dialect_utils import get_compatible_foreign_key_options


class AuditoriaUsuario(Base):
    """
    Modelo SQLAlchemy para la tabla de auditoría de usuarios.
    Registra los cambios de estado de los usuarios.
    """
    __tablename__ = "auditoria_usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id",
                                            **get_compatible_foreign_key_options(ondelete="CASCADE",
                                                                                 onupdate="CASCADE")), nullable=False)
    estado_anterior = Column(SQLAlchemyEnum(EstadoUsuarioEnum), default=EstadoUsuarioEnum.Sin_confirmar)
    estado_nuevo = Column(SQLAlchemyEnum(EstadoUsuarioEnum), default=EstadoUsuarioEnum.Sin_confirmar)
    fecha_cambio = Column(DateTime, server_default=func.now(), nullable=False)

    # Relación con la tabla de usuarios (opcional, para facilitar consultas)
    # No se define un back_populates aquí ya que usualmente no se navega
    # desde el usuario a sus entradas de auditoría directamente como una colección.
    usuario = relationship("Usuario")

    def __repr__(self):
        return f"<AuditoriaUsuario(id={self.id}, usuario_id={self.usuario_id}, fecha_cambio='{self.fecha_cambio}')>"
