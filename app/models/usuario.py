import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Enum as SQLAlchemyEnum,
    DateTime,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class TipoUsuarioEnum(str, enum.Enum):
    Cliente = "Cliente"
    Administrador = "Administrador"
    Vendedor = "Vendedor"


class EstadoUsuarioEnum(str, enum.Enum):
    Activo = "Activo"
    Inactivo = "Inactivo"
    Bloqueado = "Bloqueado"
    Eliminado = "Eliminado"
    Sin_confirmar = "Sin confirmar"


class GeneroEnum(str, enum.Enum):
    Masculino = "Masculino"
    Femenino = "Femenino"
    Otro = "Otro"


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (Index("idx_usuarios_correo", "correo"),)

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    correo = Column(String(100), nullable=False, unique=True, index=True)
    contrasena = Column(
        String(255), nullable=False
    )  # Almacena el hash de la contraseña
    telefono = Column(String(15), nullable=False, unique=True)
    fecha_nacimiento = Column(Date, nullable=False)
    genero = Column(SQLAlchemyEnum(GeneroEnum))
    tipo_usuario = Column(
        SQLAlchemyEnum(TipoUsuarioEnum), default=TipoUsuarioEnum.Cliente
    )
    estado = Column(
        SQLAlchemyEnum(
            EstadoUsuarioEnum,
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=EstadoUsuarioEnum.Sin_confirmar.value,
    )
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relaciones
    pedidos = relationship("Pedido", back_populates="usuario")
    localizaciones = relationship("LocalizacionPedido", back_populates="usuario")
    carrito_items = relationship("Carrito", back_populates="usuario")
    comentarios = relationship("Comentario", back_populates="usuario")
