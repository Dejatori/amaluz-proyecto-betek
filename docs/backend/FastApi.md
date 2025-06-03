# FastAPI: Framework Web para APIs Modernas

## ¿Qué es FastAPI?

FastAPI es un framework web moderno, rápido y de alto rendimiento para construir APIs con Python 3.7+ basado en 
estándares como OpenAPI. Combina la facilidad de uso con un rendimiento similar a NodeJS y Go, gracias a Starlette
para el manejo de solicitudes y Pydantic para la validación de datos.

## ¿Por qué usar FastAPI?

- **Alto rendimiento**: Uno de los frameworks más rápidos disponibles en Python
- **Validación automática**: Validación de datos de entrada y salida mediante Pydantic
- **Documentación automática**: Genera documentación interactiva con Swagger UI y ReDoc
- **Tipado estático**: Aprovecha el sistema de tipos de Python para mayor seguridad
- **Async/await**: Soporte nativo para código asíncrono
- **Inyección de dependencias**: Sistema incorporado para gestionar dependencias

## Estructura en nuestro proyecto

En nuestro sistema de gestión de inventario, FastAPI se estructura de la siguiente manera:

```
app/
├── api/
│   ├── endpoints/            # Endpoints de la API (productos, clientes, pedidos)
│   └── dependencies.py       # Dependencias compartidas
├── core/
│   └── config.py             # Configuración de la aplicación
├── main.py                   # Punto de entrada principal
```

## Configuración básica

```python
# app/main.py
from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API para Sistema de Gestión de Inventario",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Incluir routers
app.include_router(
    products.router, 
    prefix=f"{settings.API_V1_STR}/products", 
    tags=["products"]
)
```

## Integrando el patrón Repository

FastAPI se integra perfectamente con nuestro patrón Repository mediante inyección de dependencias:

### 1. Definir dependencias

```python
# app/api/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService


def get_product_repository(db: Session = Depends(get_db)) -> ProductRepository:
    return ProductRepository(db)


def get_product_service(
        repo: ProductRepository = Depends(get_product_repository)
) -> ProductService:
    return ProductService(repo)
```

### 2. Crear endpoints

```python
# app/api/endpoints/products.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.product import Product, ProductCreate
from app.services.product_service import ProductService
from app.api.dependencies import get_product_service

router = APIRouter()

@router.get("/", response_model=list[Product])
def get_products(
    service: ProductService = Depends(get_product_service),
    skip: int = 0,
    limit: int = 100
):
    return service.list_products(skip=skip, limit=limit)

@router.post("/", response_model=Product, status_code=201)
def create_product(
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    return service.create_product(product_data)
```

## Validación de datos con Pydantic

FastAPI utiliza Pydantic para validar los datos de entrada y salida:

```python
# app/schemas/product.py
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    price: float = Field(..., gt=0)

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    
    class Config:
        orm_mode = True  # Permite convertir objetos ORM a respuestas JSON
```

## Documentación automática

FastAPI genera automáticamente documentación interactiva:

- **Swagger UI**: Accesible en `/docs`
- **ReDoc**: Accesible en `/redoc`

## Mejores prácticas para FastAPI

1. **Estructura organizada por dominio**:
    - Agrupar endpoints relacionados en routers separados

2. **Separación de modelos y esquemas**:
    - Modelos SQLAlchemy para la base de datos
    - Esquemas Pydantic para la API

3. **Inyección de dependencias**:
    - Usar el sistema de dependencias para servicios, repositorios y bases de datos

4. **Manejo de excepciones**:
   ```python
   from fastapi import HTTPException
   
   if not product:
       raise HTTPException(status_code=404, detail="Producto no encontrado")
   ```

5. **Paginación y filtrado**:
   ```python
   @router.get("/")
   def get_products(
       skip: int = 0,
       limit: int = 100,
       category: str | None = None,
       service: ProductService = Depends(get_product_service)
   ):
       return service.list_products(skip=skip, limit=limit, category=category)
   ```

6. **Middleware para funcionalidades transversales**:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

## Autenticación y autorización

Para implementar seguridad en FastAPI:

```python
# app/core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verificar token y devolver usuario
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
```

## Manejo de tareas asíncronas

FastAPI permite operaciones asíncronas para mejorar el rendimiento:

```python
@router.get("/async-products")
async def get_products_async(
    service: ProductService = Depends(get_product_service)
):
    # Operación que no bloquea (por ejemplo, consultar desde Redis)
    return await service.list_products_async()
```

## Testing en FastAPI

```python
# tests/test_api/test_products.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_products():
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## Desarrollo vs. Producción

### Desarrollo
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

### Producción
```
# Usando Gunicorn con Uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## Integración con SQLAlchemy

FastAPI trabaja perfectamente con SQLAlchemy utilizando dependencias:

```python
from app.db.database import get_db


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product
```

## Docker y despliegue

En nuestro proyecto con Docker:

```docker
# Dockerfile
FROM python:3.9

WORKDIR /app/

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: "3.8"
services:
   api:
      build: ..
      ports:
         - "8000:8000"
      depends_on:
         - db
      environment:
         - MYSQL_SERVER=db
         - MYSQL_USER=app_user
         - MYSQL_PASSWORD=app_password
         - MYSQL_DB=inventory
```

## Rendimiento y monitoreo

Para monitorear y optimizar el rendimiento:

- Utiliza la versión asíncrona de SQLAlchemy cuando sea posible
- Implementa caché con Redis para consultas frecuentes
- Monitorea con herramientas como Prometheus y Grafana
- Utiliza logging estructurado para seguimiento y diagnóstico