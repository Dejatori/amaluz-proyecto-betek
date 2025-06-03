1.  **Configuración Inicial del Entorno y Proyecto:**
    *   Crea y activa un entorno virtual (`python -m venv venv`, `source venv/bin/activate` o 
        `venv\Scripts\activate` en Windows).
    *   Instala las dependencias: `pip install -r requirements.txt` y `pip install -r requirements-dev.txt`.
    *   Establece la estructura básica del proyecto FastAPI como se describe en `docs/project_structure.md` 
        (`app/main.py`, `app/core/config.py`, etc.).
    *   Configura las variables de entorno (`.env`) para la base de datos y secretos (JWT) usando `pydantic-settings`
        en `app/core/config.py`.
    *   Implementa la configuración de la sesión de base de datos asíncrona (`app/db/session.py`) usando 
        `create_async_engine` de SQLAlchemy y `aiomysql`. Asegúrate de que use la URL de la
        base de datos desde la configuración.

2.  **Inicialización y Primera Migración de Base de Datos:**
    *   Inicializa Alembic: `alembic init alembic`.
    *   Configura `alembic.ini` y `alembic/env.py` para que usen la URL de la base de datos de tu configuración y
        reconozcan los modelos SQLAlchemy (importando `Base` de `app/db/base.py` y los modelos).
    *   Define los primeros modelos SQLAlchemy esenciales (ej. `Usuario`, `Producto` en `app/models/`) con sus 
        columnas básicas, basándote en `docs/database/schema.md`.
    *   Genera la primera migración: `alembic revision --autogenerate -m "Initial database schema"`.
        Revisa el script generado en `alembic/versions/`.
    *   Aplica la migración para crear las tablas en tu base de datos MySQL: `alembic upgrade head`.

3.  **Implementación de la Primera "Vertical Slice" (Ej: Productos):**
    *   **Schemas (Pydantic):** Define los esquemas Pydantic necesarios para la entidad `Producto` en 
        `app/schemas/product.py` (ej. `ProductCreate`, `ProductUpdate`, `ProductOut`).
    *   **Repositorio:** Crea `app/repositories/product_repository.py`. Implementa métodos CRUD básicos
        (ej. `create`, `get_by_id`, `get_all`) usando operaciones `async` con la sesión de SQLAlchemy inyectada.
        Considera crear un `BaseRepository` genérico en `app/repositories/base.py` para reutilizar lógica común.
    *   **Servicio:** Crea `app/services/product_service.py`. Inyecta `ProductRepository`. Implementa la lógica de 
        negocio inicial (que puede ser simplemente llamar a los métodos del repositorio al principio).
    *   **API Endpoint:** Crea `app/api/endpoints/products.py`. Define un `APIRouter`. Implementa los endpoints
        RESTful básicos (POST para crear, GET para leer lista y por ID). Usa `Depends` para inyectar el 
        `ProductService` y la sesión de BD. Utiliza los schemas Pydantic para validación de entrada y serialización 
        de salida (`response_model`). Registra este router en `app/main.py`.
    *   **(Opcional pero recomendado) Pruebas:** Escribe pruebas unitarias/integración básicas para el repositorio,
        servicio y endpoint usando `pytest`. Puedes usar `httpx` para probar los endpoints de la API.

4.  **Configuración de Autenticación (JWT):**
    *   Implementa la lógica para crear y verificar tokens JWT en `app/core/security.py` usando `python-jose` 
        y `passlib` para el hashing de contraseñas.
    *   Crea los endpoints de autenticación (ej. `/login/token`) en un router dedicado
        (ej. `app/api/endpoints/login.py`).
    *   Define dependencias en `app/api/deps.py` para obtener el usuario actual a partir del token JWT 
        (`get_current_user`).
    *   Protege los endpoints que lo requieran (ej. crear/modificar productos) usando estas dependencias.

5.  **Iterar:**
    *   Repite el paso 3 para las siguientes entidades (Usuarios, Pedidos, etc.), construyendo la aplicación 
        de forma incremental.
    *   Ejecuta continuamente las pruebas y herramientas de calidad de código (`ruff`, `black`, `isort`).
    *   Refactoriza según sea necesario.

6.  **Iniciar el Servidor:**
    *   Usa `uvicorn` para iniciar el servidor de desarrollo: `uvicorn app.main:app --reload`.
    *   Asegúrate de que la aplicación esté corriendo y prueba los endpoints usando Postman o Swagger UI 
        (`/docs`).

7.  **Iniciar Celery Tasks:**
    *   Configura Celery en `app/core/celery_app.py` y define tareas en `app/core/tasks.py`.
    *   Asegúrate de que Celery esté corriendo y conectado a tu base de datos y broker (ej. Redis).
    *   Usa `celery -A app.core.celery_app worker --pool=solo --loglevel=INFO` para iniciar el worker de Celery.
    *   Implementa tareas asíncronas para operaciones que puedan ser demoradas (ej. envío de correos, procesamiento 
        de datos).

8.  **Ejecutar prubeas MySQL en Docker:**
    *   En el archivo `docker-compose.test.mysql.yml`, configura el servicio de MySQL para pruebas.
    *   Usa 
        `docker-compose -f docker-compose.test.mysql.yml up --build --abort-on-container-exit --exit-code-from tests`
        para iniciar el contenedor de MySQL y ejecutar las pruebas.

9.  **Ejecutar pruebas SQLServer en Docker:**
    *   En el archivo `docker-compose.test.sqlserver.yml`, configura el servicio de SQL Server para pruebas.
    *   Usa 
        `docker-compose -f docker-compose.test.sqlserver.yml up --build --abort-on-container-exit --exit-code-from tests`
        para iniciar el contenedor de SQL Server y ejecutar las pruebas.
