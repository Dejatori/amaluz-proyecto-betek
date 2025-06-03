# SQLAlchemy: ORM para Python

## ¿Qué es SQLAlchemy?

SQLAlchemy es un ORM (Object Relational Mapper) para Python que proporciona una abstracción completa sobre bases de 
datos relacionales. Permite trabajar con objetos Python en lugar de SQL directo, facilitando operaciones de base de
datos y mejorando el mantenimiento del código.

## ¿Por qué usar SQLAlchemy?

- **Abstracción de la base de datos**: Permite cambiar de motor de base de datos sin modificar el código
- **Modelado con clases Python**: Define tablas como clases y registros como objetos
- **Expresividad**: Soporta consultas complejas con sintaxis Pythonic
- **Transacciones integradas**: Manejo automático de sesiones y transacciones
- **Seguridad**: Previene inyecciones SQL mediante parametrización
- **Mapeo de relaciones**: Gestiona relaciones entre tablas (uno a uno, uno a muchos, muchos a muchos)

## Estructura en nuestro proyecto

```
app/
├── db/
│   ├── __init__.py
│   ├── base.py        # Base declarativa común para modelos
│   └── session.py     # Configuración de conexión y sesiones
├── models/
│   ├── __init__.py
│   ├── product.py
│   ├── customer.py
│   └── order.py
```

## Configuración básica

```python
# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Definición de modelos

Los modelos representan tablas en la base de datos:

```python
# app/models/product.py
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    order_items = relationship("OrderItem", back_populates="product")
```

## Relaciones entre modelos

SQLAlchemy permite definir relaciones entre tablas:

### Relación uno a muchos

```python
# app/models/customer.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación uno a muchos con Order
    orders = relationship("Order", back_populates="customer")
```

```python
# app/models/order.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_date = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, default=0.0)
    
    # Relación con Customer
    customer = relationship("Customer", back_populates="orders")
    
    # Relación con OrderItem
    items = relationship("OrderItem", back_populates="order")
```

### Relación muchos a muchos

```python
# app/models/order_item.py
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    
    # Relaciones
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
```

## Implementación del Patrón Repository

El patrón Repository separa la lógica de acceso a datos de la lógica de negocio:

```python
# app/repositories/base_repository.py
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: Any) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def remove(self, *, id: int) -> ModelType:
        obj = self.db.query(self.model).get(id)
        self.db.delete(obj)
        self.db.commit()
        return obj
```

Implementación específica para productos:

```python
# app/repositories/product_repository.py
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product, ProductCreate, ProductUpdate]):
    def __init__(self, db: Session):
        super().__init__(Product, db)

    def get_by_name(self, name: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.name == name).first()

    def get_active(self, *, skip: int = 0, limit: int = 100) -> List[Product]:
        return self.db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()
```

## Operaciones comunes con SQLAlchemy

### Consultas básicas

```python
# Obtener todos los productos
products = db.query(Product).all()

# Obtener producto por ID
product = db.query(Product).filter(Product.id == product_id).first()

# Filtrar productos por precio
expensive_products = db.query(Product).filter(Product.price > 1000).all()

# Ordenar productos por nombre
sorted_products = db.query(Product).order_by(Product.name).all()

# Contar productos
product_count = db.query(Product).count()
```

### Consultas con relaciones

```python
# Obtener cliente con sus pedidos (carga perezosa)
customer = db.query(Customer).filter(Customer.id == customer_id).first()
customer_orders = customer.orders  # Se carga cuando se accede

# Carga eager (inmediata) con join
from sqlalchemy.orm import joinedload

customer = (
    db.query(Customer)
    .options(joinedload(Customer.orders))
    .filter(Customer.id == customer_id)
    .first()
)
```

### Consultas avanzadas

```python
from sqlalchemy import func, desc, or_, and_

# Agrupar y agregar
sales_by_product = (
    db.query(
        Product.name, 
        func.sum(OrderItem.quantity * OrderItem.unit_price).label("total_sales")
    )
    .join(OrderItem.product)
    .group_by(Product.name)
    .order_by(desc("total_sales"))
    .all()
)

# Consultas con múltiples condiciones
results = (
    db.query(Product)
    .filter(
        and_(
            Product.is_active == True,
            or_(
                Product.price < 100,
                Product.stock > 10
            )
        )
    )
    .all()
)
```

## Transacciones

```python
# Usando contexto de transacción explícito
from sqlalchemy.orm import Session

def transfer_stock(db: Session, from_product_id: int, to_product_id: int, amount: int):
    try:
        # Obtener productos
        from_product = db.query(Product).filter(Product.id == from_product_id).with_for_update().first()
        to_product = db.query(Product).filter(Product.id == to_product_id).with_for_update().first()
        
        # Verificar stock suficiente
        if from_product.stock < amount:
            raise ValueError("Stock insuficiente")
        
        # Transferir stock
        from_product.stock -= amount
        to_product.stock += amount
        
        # Confirmar transacción
        db.commit()
        return True
    except Exception as e:
        # Revertir en caso de error
        db.rollback()
        raise e
```

## Optimizaciones de rendimiento

### Consultas parciales (select)

```python
# Seleccionar solo las columnas necesarias
names = db.query(Product.name).all()
```

### Paginación

```python
# Paginar resultados (útil para API)
page = 1
page_size = 25
offset = (page - 1) * page_size

products = db.query(Product).offset(offset).limit(page_size).all()
```

### Consultas "solo para lectura"

```python
# Para consultas de solo lectura (sin trackeo de cambios)
products = db.query(Product).execution_options({"autoflush": False}).all()
```

## Integración con FastAPI

SQLAlchemy se integra con FastAPI mediante inyección de dependencias:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.product_repository import ProductRepository
from app.schemas.product import Product, ProductCreate

router = APIRouter()


@router.get("/{product_id}", response_model=Product)
def get_product(
        product_id: int,
        db: Session = Depends(get_db)
):
    repository = ProductRepository(db)
    product = repository.get(id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.post("/", response_model=Product)
def create_product(
        product_in: ProductCreate,
        db: Session = Depends(get_db)
):
    repository = ProductRepository(db)
    return repository.create(obj_in=product_in)
```

## Integración con Alembic

SQLAlchemy funciona con Alembic para gestionar migraciones:

1. En los modelos, definimos la estructura de tablas
2. Alembic detecta cambios entre los modelos y la base de datos
3. Genera migraciones automáticamente con `alembic revision --autogenerate`
4. Aplica las migraciones con `alembic upgrade head`

## Mejores prácticas

1. **Usar sesiones cortas**: Abrir sesiones solo cuando se necesitan y cerrarlas rápidamente
2. **Validar datos**: Usar Pydantic antes de insertar datos en SQLAlchemy
3. **Relaciones perezosas**: Usar lazy loading por defecto y eager loading cuando sea necesario
4. **Caché**: Implementar caché para consultas frecuentes y pesadas
5. **Índices**: Definir índices en columnas utilizadas en filtros y joins
6. **Pool de conexiones**: Configurar adecuadamente el pool para manejar cargas variables
7. **Evitar las N+1 consultas**: Usar `joinedload` para cargar relaciones eficientemente

## Ejemplo completo de configuración

```python
# app/db/base_repository.py
from app.db.database import Base

# Importar todos los modelos para que Alembic los detecte
from app.models.product import Product
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem

# Este archivo se usa para que Alembic pueda importar todos los modelos
```

Esta documentación te ayudará a entender y trabajar con SQLAlchemy en tu sistema de gestión de inventario, siguiendo 
las mejores prácticas y patrones establecidos.