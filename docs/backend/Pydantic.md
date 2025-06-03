# Pydantic: Validación y Serialización de Datos para Python

## ¿Qué es Pydantic?

Pydantic es una biblioteca de Python para la validación de datos y gestión de configuraciones utilizando anotaciones 
de tipos. Permite definir la estructura, tipos y restricciones de los datos mediante clases Python, facilitando la 
validación, serialización y documentación automática.

## ¿Por qué usar Pydantic?

- **Validación basada en tipos**: Aprovecha las anotaciones de tipos de Python para validar datos
- **Conversión automática**: Convierte tipos de datos de entrada al tipo especificado cuando es posible
- **Mensajes de error claros**: Proporciona mensajes de error detallados cuando la validación falla
- **Integración perfecta con FastAPI**: Es la biblioteca estándar para validación en FastAPI
- **Serialización a JSON**: Convierte modelos a JSON para respuestas de API
- **Rendimiento optimizado**: Implementación en parte con Rust para máxima velocidad

## Estructura en nuestro proyecto

```
app/
├── schemas/            # Esquemas Pydantic para validación y serialización
│   ├── __init__.py
│   ├── product.py
│   ├── customer.py
│   └── order.py
├── core/
│   └── config.py       # Configuración basada en Pydantic
```

## Definición de esquemas básicos

Los esquemas Pydantic definen la estructura de los datos de entrada y salida:

```python
# app/schemas/product.py
from typing import Optional
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del producto")
    description: Optional[str] = Field(None, max_length=500, description="Descripción detallada")
    price: float = Field(..., gt=0, description="Precio unitario del producto")
    stock: int = Field(0, ge=0, description="Cantidad disponible en inventario")

class ProductCreate(ProductBase):
    # Campos adicionales solo para creación
    pass

class ProductUpdate(BaseModel):
    # Todos los campos son opcionales para actualizaciones parciales
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)

class Product(ProductBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True  # Permite conversión desde objetos ORM
```

## Validadores personalizados

Pydantic permite definir validadores personalizados para lógica de negocio específica:

```python
# app/schemas/order.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)

class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate]
    
    @field_validator("items")
    def validate_items(cls, v):
        if not v or len(v) < 1:
            raise ValueError("Un pedido debe tener al menos un producto")
        return v
    
    @model_validator(mode="after")
    def validate_order(self):
        # Podríamos añadir validaciones complejas aquí
        return self
```

## Integración con FastAPI

Pydantic se integra perfectamente con FastAPI para validar datos de entrada y documentar la API:

```python
# app/api/endpoints/products.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.services.product_service import ProductService
from app.api.dependencies import get_product_service

router = APIRouter()

@router.post("/", response_model=Product, status_code=201)
def create_product(
    product_in: ProductCreate,  # Pydantic valida automáticamente los datos de entrada
    service: ProductService = Depends(get_product_service)
):
    return service.create_product(product_in)

@router.get("/", response_model=List[Product])
def list_products(
    skip: int = 0,
    limit: int = 100, 
    service: ProductService = Depends(get_product_service)
):
    return service.list_products(skip=skip, limit=limit)
```

## Configuraciones con Pydantic

Pydantic también es útil para gestionar configuraciones:

```python
# Ejemplo simplificado de app/core/config.py
from pydantic import AnyHttpUrl, MySQLDsn, BaseSettings, validator
from typing import List, Union, Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sistema de Gestión de Inventario"
    
    # Conexión base de datos
    MYSQL_SERVER: str = "localhost"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = "inventory"
    SQLALCHEMY_DATABASE_URI: Optional[MySQLDsn] = None
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v, values):
        if isinstance(v, str):
            return v
        return MySQLDsn.build(
            scheme="mysql+pymysql",
            user=values.get("MYSQL_USER"),
            password=values.get("MYSQL_PASSWORD"),
            host=values.get("MYSQL_SERVER"),
            path=f"/{values.get('MYSQL_DB') or ''}"
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

## Manejo de tipos complejos

Pydantic soporta tipos complejos y anidados:

```python
# app/schemas/dashboard.py
from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field

class TimeFrame(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

class SalesSummary(BaseModel):
    period: date
    total: float
    count: int

class DashboardData(BaseModel):
    sales_by_time: Dict[TimeFrame, List[SalesSummary]]
    top_products: List[Dict[str, Union[int, str, float]]]
    inventory_alerts: List[Dict[str, Union[int, str]]]
    updated_at: datetime = Field(default_factory=datetime.now)
```

## Serialización y deserialización

Pydantic facilita la conversión entre formatos:

```python
# Convertir a diccionario
product_dict = product_model.model_dump()

# Convertir a JSON
product_json = product_model.model_dump_json()

# Crear desde diccionario
product = Product.model_validate(product_dict)

# Crear desde JSON
product = Product.model_validate_json(product_json)

# Actualización parcial
updated_product = product.model_copy(update=product_update.model_dump(exclude_unset=True))
```

## Integración con SQLAlchemy

Pydantic trabaja con los modelos de SQLAlchemy mediante `from_attributes`:

```python
# Convertir de objeto SQLAlchemy a Pydantic
db_product = product_repository.get(id=1)
product_schema = Product.model_validate(db_product)

# Con SQLAlchemy y FastAPI
@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(ProductModel).get(product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    # FastAPI convierte automáticamente el modelo SQLAlchemy a Pydantic
    return db_product
```

## Validación avanzada

```python
# app/schemas/inventory.py
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class InventoryAdjustment(BaseModel):
    product_id: int
    quantity: int
    reason: str
    adjustment_date: date = Field(default_factory=date.today)
    reference_document: Optional[str] = None
    
    @field_validator("quantity")
    def quantity_cannot_be_zero(cls, v):
        if v == 0:
            raise ValueError("La cantidad no puede ser cero")
        return v
        
    @field_validator("reason")
    def reason_must_be_valid(cls, v):
        valid_reasons = ["recepción", "venta", "devolución", "ajuste", "daño"]
        if v.lower() not in valid_reasons:
            raise ValueError(f"Razón no válida. Debe ser una de: {', '.join(valid_reasons)}")
        return v
```

## Mejores prácticas

1. **Organizar esquemas jerárquicamente**: Usar clases base para compartir campos comunes
2. **Separar modelos de entrada y salida**: Usar diferentes clases para creación, actualización y respuestas
3. **Usar campos opcionales para actualizaciones**: En esquemas de actualización, hacer los campos opcionales
4. **Documentar los campos**: Usar `Field(description="...")` para generar documentación clara
5. **Validar temprano**: Validar los datos lo antes posible en el flujo de la aplicación
6. **Campos calculados**: Usar propiedades `@property` para campos calculados dinámicamente
7. **Mantener esquemas delgados**: Evitar lógica compleja en los esquemas, delegarla a los servicios

## Ejemplo completo en el contexto del proyecto

```python
# app/schemas/complete_order.py
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    total: float
    
    @property
    def calculated_total(self) -> float:
        return self.quantity * self.unit_price

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customer_id: int

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    
    @field_validator("items")
    def validate_items(cls, v):
        if not v or len(v) < 1:
            raise ValueError("Un pedido debe tener al menos un producto")
        return v

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None

class Order(OrderBase):
    id: int
    order_date: datetime
    status: OrderStatus
    items: List[OrderItem]
    total: float
    
    @model_validator(mode="after")
    def calculate_total(self):
        self.total = sum(item.calculated_total for item in self.items)
        return self

    class Config:
        from_attributes = True
```