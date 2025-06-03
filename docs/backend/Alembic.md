# Alembic: Herramienta de Migración de Bases de Datos

## ¿Qué es Alembic?

Alembic es una herramienta de migración de bases de datos para SQLAlchemy que ayuda a gestionar los cambios en el 
esquema de tu base de datos a lo largo del tiempo. Proporciona una manera de actualizar incrementalmente tu esquema 
de base de datos mientras se preservan los datos existentes, rastrear estos cambios en el control de versiones y 
coordinar las implementaciones en entornos de desarrollo, pruebas y producción.

## ¿Por qué usar Alembic?

-   **Control de versiones para esquemas de bases de datos**: Rastrea todos los cambios de la base de datos en tu repositorio.
-   **Coordinación de equipos**: Todos los desarrolladores trabajan con versiones de esquema consistentes.
-   **Evolución segura de la base de datos**: Aplica cambios incrementalmente sin pérdida de datos.
-   **Consistencia del entorno**: Mismo proceso de migración en desarrollo, pruebas y producción.

## Requisitos previos

Antes de usar Alembic, asegúrate de tener:

-   SQLAlchemy instalado (`pip install sqlalchemy`)
-   Alembic instalado (`pip install alembic`)
-   Modelos de SQLAlchemy definidos en tu proyecto
-   Conexión a la base de datos configurada

## Configuración e Instalación

### 1. Inicializar Alembic

Desde el directorio raíz de tu proyecto, ejecuta:

```bash
alembic init alembic
```

Esto crea un directorio `alembic` con los siguientes archivos:

-   `alembic.ini`: Archivo de configuración principal.
-   `alembic/env.py`: Configuración del entorno.
-   `alembic/script.py.mako`: Plantilla para scripts de migración.
-   `alembic/versions/`: Directorio donde se almacenarán los archivos de migración.

### 2. Configurar la Conexión a la Base de Datos

Edita `alembic.ini` para establecer la URL de conexión de tu base de datos:

```ini
# Reemplaza con tu cadena de conexión
sqlalchemy.url = mysql+pymysql://root:@localhost/inventory
```

Alternativamente, puedes usar la configuración de nuestra aplicación:

```ini
# Para el entorno Docker, usa:
sqlalchemy.url = mysql+pymysql://app_user:app_password@db/inventory
```

### 3. Configurar el Acceso a los Modelos

Edita `alembic/env.py` para importar tus modelos de SQLAlchemy:

```python
import os
import sys
from app.core.config import settings
from app.models.base import Base
from app.models.product import Product
from app.models.customer import Customer
from app.models.order import Order

# Añade la raíz del proyecto a la ruta de Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Establece los metadatos objetivo a tus modelos de SQLAlchemy
target_metadata = Base.metadata
```

## Uso de Alembic

### Comandos Comunes

```bash
# Genera una migración automáticamente basada en los cambios del modelo
alembic revision --autogenerate -m "Descripción de los cambios"

# Aplica todas las migraciones pendientes
alembic upgrade head

# Aplica solo la siguiente migración
alembic upgrade +1

# Retrocede una migración
alembic downgrade -1

# Retrocede a una migración específica
alembic downgrade <revision_id>

# Muestra la versión de migración actual
alembic current

# Muestra el historial de migraciones
alembic history
```

### Flujo de Trabajo Paso a Paso

1.  **Crea o modifica tus modelos de SQLAlchemy**

    ```python
    # app/models/product.py
    from sqlalchemy import Column, Integer, String, Float
    from app.models.base import Base

    class Product(Base):
        __tablename__ = "products"

        id = Column(Integer, primary_key=True, index=True)
        name = Column(String(100), nullable=False)
        description = Column(String(500))
        price = Column(Float, nullable=False)
    ```

2.  **Genera una migración**

    ```bash
    alembic revision --autogenerate -m "Añadir modelo de producto"
    ```

3.  **Revisa el archivo de migración generado**

    Siempre revisa el archivo generado en `alembic/versions/` antes de aplicarlo para asegurarte de que hace lo que esperas.

4.  **Aplica la migración**

    ```bash
    alembic upgrade head
    ```

5.  **Confirma tanto los cambios del modelo como los archivos de migración en el control de versiones**

## Ejemplo: Añadir un Nuevo Campo

1.  **Modifica tu modelo**

    ```python
    # app/models/product.py
    from sqlalchemy import Column, Integer, String, Float, Boolean
    from app.models.base import Base

    class Product(Base):
        __tablename__ = "products"

        id = Column(Integer, primary_key=True, index=True)
        name = Column(String(100), nullable=False)
        description = Column(String(500))
        price = Column(Float, nullable=False)
        is_active = Column(Boolean, default=True)  # Nuevo campo
    ```

2.  **Genera y aplica la migración**

    ```bash
    alembic revision --autogenerate -m "Añadir campo is_active a productos"
    alembic upgrade head
    ```

## Mejores Prácticas

1.  **Siempre revisa las migraciones autogeneradas** antes de aplicarlas.
2.  **Nunca modifiques los archivos de migración** después de que se hayan aplicado a cualquier entorno.
3.  **Controla la versión de todos los archivos de migración** junto con tu código.
4.  **Realiza copias de seguridad de tu base de datos** antes de aplicar migraciones en producción.
5.  **Prueba las migraciones** en desarrollo/staging antes de aplicarlas a producción.
6.  **Utiliza nombres de migración descriptivos** para documentar los cambios de tu esquema.
7.  **Incluye migraciones de datos** cuando sea necesario (por ejemplo, rellenar nuevas columnas).

## Integración con FastAPI

En tu aplicación FastAPI, evita la creación directa de tablas con SQLAlchemy:

```python
# Comenta o elimina esta línea de main.py
# base.Base.metadata.create_all(bind=engine)
```

En su lugar, utiliza Alembic para gestionar todos los cambios del esquema de la base de datos.

## Solución de Problemas

-   **Tablas faltantes**: Asegúrate de que todos los modelos estén importados en `env.py`.
-   **Errores de conexión**: Verifica la cadena de conexión de la base de datos en `alembic.ini`.
-   **Errores de importación**: Comprueba que tu ruta de Python incluya la raíz de tu proyecto.
-   **Migraciones fallidas**: Utiliza `alembic downgrade` para revertir, corregir y volver a intentar.

## Consideraciones de Implementación con Docker

Cuando uses Alembic con Docker:

1.  Ejecuta las migraciones como parte de tu script de inicio del contenedor.
2.  Asegúrate de que la base de datos esté lista antes de que se ejecuten las migraciones.
3.  Añade una comprobación de estado para verificar que las migraciones se completaron correctamente.

```bash
# Ejemplo de comando de inicio para Docker
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```
