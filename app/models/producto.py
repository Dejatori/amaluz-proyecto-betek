import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DECIMAL,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    DateTime,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.db.dialect_utils import get_compatible_foreign_key_options


class CategoriaProductoEnum(str, enum.Enum):
    Velas_Aromaticas = "Velas Aromáticas"
    Velas_Decorativas = "Velas Decorativas"
    Velas_Artesanales = "Velas Artesanales"
    Velas_Personalizadas = "Velas Personalizadas"
    Velas_de_Recordatorio = "Velas de Recordatorio"


class FraganciaProductoEnum(str, enum.Enum):
    Lavanda = "Lavanda"
    Rosa = "Rosa"
    Citricos = "Cítricos"
    Vainilla = "Vainilla"
    Chocolate = "Chocolate"
    Eucalipto = "Eucalipto"
    Menta = "Menta"
    Canela = "Canela"
    Cafe = "Café"
    Tropical = "Tropical"
    Jazmin = "Jazmín"
    Bebe = "Bebé"
    Sandalo = "Sándalo"
    Pino = "Pino"
    Naturaleza = "Naturaleza"
    Sofe = "Sofe"
    Citricos_Frescos = "Cítricos Frescos"
    Frutos_Rojos = "Frutos Rojos"
    Frutos_Amarillos = "Frutos Amarillos"
    Romero = "Romero"
    Especias = "Especias"
    Chicle = "Chicle"
    Coco = "Coco"
    Tabaco_Chanelle = "Tabaco & Chanelle"


class EstadoProductoEnum(str, enum.Enum):
    Activo = "Activo"
    Inactivo = "Inactivo"


class Producto(Base):
    __tablename__ = "productos"
    __table_args__ = (
        Index("idx_productos_categoria", "categoria"),
        Index("idx_productos_fragancia", "fragancia"),
        Index("idx_productos_estado", "estado"),
    )

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    precio_venta = Column(DECIMAL(10, 2), nullable=False)
    categoria = Column(
        SQLAlchemyEnum(
            CategoriaProductoEnum,
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    peso = Column(DECIMAL(5, 2), nullable=False)
    dimensiones = Column(String(50), nullable=False)
    imagen_url = Column(String(255), nullable=False)
    fragancia = Column(
        SQLAlchemyEnum(
            FraganciaProductoEnum,
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    periodo_garantia = Column(Integer, nullable=False, default=90)
    estado = Column(
        SQLAlchemyEnum(EstadoProductoEnum),
        nullable=False,
        default=EstadoProductoEnum.Activo,
    )
    precio_proveedor = Column(DECIMAL(10, 2), nullable=False)
    proveedor_id = Column(
        Integer,
        ForeignKey(
            "proveedores.id",
            **get_compatible_foreign_key_options(
                ondelete="SET NULL", onupdate="CASCADE"
            )
        ),
    )
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relaciones
    proveedor = relationship("Proveedor", back_populates="productos")
    inventario = relationship(
        "Inventario", back_populates="producto", uselist=False
    )  # One-to-one
    detalles_pedido = relationship("DetallePedido", back_populates="producto")
    carrito_items = relationship("Carrito", back_populates="producto")
    comentarios = relationship("Comentario", back_populates="producto")
