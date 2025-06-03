## Arquitectura Detallada del Sistema

Esta arquitectura sigue las directrices y tecnologías definidas en `docs/project.md`, integrando FastAPI, SQLAlchemy, 
Pydantic, JWT, Redis, MySQL en el backend, y React, TypeScript, Axios, React Query, Vite, Tailwind CSS en el frontend.

### 1. Base de Datos (MySQL)

*   **Esquema:** El esquema relacional ya está definido en `db/schema.sql` y documentado en `docs/database/schema.md`. 
* Incluye tablas para `usuarios`, `proveedores`, `productos`, `inventario`, `localizacion_pedido`, `pedidos`, 
  `detalle_pedido`, `carrito`, `comentarios`, `envios`, `descuentos` y
  sus respectivas tablas de auditoría.
*   **ORM:** SQLAlchemy se utiliza para mapear estas tablas a modelos Python (clases definidas probablemente
    en `app/models/`).
*   **Migraciones:** Alembic gestionará las evoluciones del esquema de la base de datos.
    Se configurará para generar y aplicar scripts de migración.

### 2. Backend (FastAPI)

#### a. Capa de Acceso a Datos (Patrón Repository)

*   **Objetivo:** Abstraer las operaciones de base de datos (CRUD) de la lógica de negocio.
*   **Implementación:**
    *   Se creará un repositorio base genérico (si aplica) y repositorios específicos para cada entidad principal
        (ej. `UsuarioRepository`, `ProductoRepository`, `PedidoRepository`) en un directorio como `app/repositories/`.
    *   Cada repositorio recibirá una `Session` de SQLAlchemy a través de inyección de dependencias para 
        interactuar con la base de datos.
    *   Ejemplo (`ProductRepository`):
        ```python
        # app/repositories/producto_repository.py
        from app.models.producto import Producto
        from app.schemas.producto import ProductoCreate, ProductoUpdate
        from app.repositories.base_repository import BaseRepository
    
        class ProductoRepository(BaseRepository[Producto, ProductoCreate, ProductoUpdate]):
        pass
    
        producto_repository = ProductoRepository(Producto)
        ```

#### b. Capa de Lógica de Negocio (Servicios)

*   **Objetivo:** Contener la lógica de negocio específica de la aplicación, orquestando operaciones entre diferentes
    repositorios si es necesario.
*   **Implementación:**
    *   Se crearán clases de servicio para cada dominio funcional 
        (ej. `ProductoService`, `PedidoService`, `AutenticacionService`) en un directorio como `app/services/`.
    *   Los servicios dependerán de uno o más repositorios, inyectados en su constructor.
    *   Utilizarán esquemas Pydantic (`app/schemas/`) para la validación y transferencia de datos entre
        la API y los repositorios.
    *   Ejemplo (`ProductService`):
        ```python
        # app/services/producto_service.py
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.repositories.producto_repository import producto_repository
        from app.schemas.producto import ProductoCreate, ProductoUpdate
    
        class ProductoService:
            async def get(self, db: AsyncSession, id: int):
                return await producto_repository.get(db, id)
    
            async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100):
                return await producto_repository.get_multi(db, skip=skip, limit=limit)
    
            async def create(self, db: AsyncSession, obj_in: ProductoCreate):
                return await producto_repository.create(db, obj_in=obj_in)
    
            async def update(self, db: AsyncSession, db_obj, obj_in: ProductoUpdate):
                return await producto_repository.update(db, db_obj=db_obj, obj_in=obj_in)
    
            async def remove(self, db: AsyncSession, id: int):
                return await producto_repository.remove(db, id=id)
    
        producto_service = ProductoService()
        ```

#### c. Capa de API (FastAPI Endpoints)

*   **Objetivo:** Exponer la funcionalidad del backend a través de una API RESTful.
*   **Implementación:**
    *   Se organizarán los endpoints en routers por entidad/funcionalidad 
        (ej. `app/api/endpoints/productos.py`, `usuarios.py`, `pedidos.py`), como ya se ve en `app/main.py`.
    *   Se utilizará la inyección de dependencias de FastAPI (`Depends`) para obtener instancias de los servicios 
        y la sesión de base de datos (`get_db`).
    *   **Autenticación:** Se implementará un sistema de autenticación basado en JWT (OAuth2PasswordBearer) para
        proteger los endpoints que lo requieran. Un servicio `AutenticacionService`
        manejará la creación y verificación de tokens.
    *   **Validación:** FastAPI usará automáticamente los esquemas Pydantic definidos en los endpoints para validar
        los datos de entrada (cuerpo de la solicitud, parámetros de consulta) y serializar los datos de salida.
    *   **Caching (Redis):** Se puede implementar un caché con Redis para endpoints de lectura frecuente 
        (ej. lista de productos, detalles de un producto). Se podría usar una dependencia de FastAPI o 
        un decorador para gestionar el caché.
    *   Ejemplo (`productos.py`):
        ```python
        # app/api/endpoints/productos.py
        from fastapi import APIRouter, Depends, HTTPException
        from sqlalchemy.orm import Session
        from app.schemas.producto import Producto, ProductoCreate # Esquemas Pydantic
        from app.services.producto_service import ProductoService
        from app.repositories.producto_repository import ProductoRepository
        from app.api import dependencies # Módulo para dependencias (get_db, get_current_user, etc.)

        router = APIRouter()

        # Dependencia para obtener el servicio (inyecta repo que a su vez obtiene db)
        def get_producto_service(db: Session = Depends(dependencies.get_db)) -> ProductoService:
            repo = ProductoRepository(db)
            return ProductoService(producto_repo=repo)

        @router.get("/", response_model=list[Producto])
        def read_productos(
            skip: int = 0,
            limit: int = 100,
            service: ProductoService = Depends(get_producto_service)
            # current_usuario: models.Usuario = Depends(deps.get_current_active_usuario) # Ejemplo seguridad
        ):
            """
            Obtener productos.
            """
            # Aquí se podría implementar caching con Redis
            productos = service.get_productos(skip=skip, limit=limit)
            return productos

        @router.post("/", response_model=Producto, status_code=201)
        def create_producto(
            *,
            producto_in: ProductoCreate,
            service: ProductoService = Depends(get_producto_service)
            # current_user: models.Usuario = Depends(deps.get_current_active_superusuario) # Ejemplo seguridad
        ):
            """
            Crear un nuevo producto.
            """
            producto = service.create_producto(producto_in=producto_in)
            return producto

        @router.get("/{producto_id}", response_model=Producto)
        def read_producto(
            producto_id: int,
            service: ProductoService = Depends(get_producto_service)
            # current_usuario: models.Usuario = Depends(deps.get_current_active_usuario)
        ):
            """
            Obtener un producto por ID.
            """
            producto = service.get_producto(producto_id=producto_id)
            if not producto:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            return producto

        # ... otros endpoints (PUT, DELETE)
        ```

### 3. Frontend (React + TypeScript)

*   **Framework/Librería:** React con TypeScript.
*   **Build Tool:** Vite para un desarrollo y construcción rápidos.
*   **Estilos:** Tailwind CSS para un diseño basado en utilidades.
*   **Llamadas API:** Axios para realizar solicitudes HTTP a la API de FastAPI. 
    Se configurará una instancia base de Axios (`src/services/api.ts` o similar).
*   **Gestión de Estado del Servidor:** React Query (`@tanstack/react-query`) para gestionar el fetching, caching, 
    sincronización y actualización de datos del servidor, reduciendo la complejidad del manejo manual del estado.
*   **Estructura:** Seguirá la estructura propuesta en `docs/project.md`
    (`components`, `pages`, `services`, `hooks`, `types`).
*   **Tipos:** Se definirán interfaces TypeScript (`src/types/`) que coincidan con los esquemas 
    Pydantic del backend para asegurar la consistencia de los datos.

### 4. Visualización (Power BI)

*   Power BI se conectará a la base de datos MySQL (preferiblemente a una réplica de lectura si el volumen de
    datos es alto) o consumirá datos a través de endpoints específicos de la API FastAPI diseñados para reporting.
*   Se crearán dashboards interactivos para visualizar métricas clave de ventas, inventario, clientes, etc.

Esta arquitectura proporciona una separación clara de responsabilidades, facilita la mantenibilidad y escalabilidad,
y aprovecha las fortalezas de las tecnologías seleccionadas.