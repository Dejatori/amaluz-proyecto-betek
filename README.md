## Descripción General del Proyecto

**Gestión de Comercio Online de Velas** es una aplicación diseñada para administrar y operar una tienda
online de velas. El sistema ofrece una API robusta basada en Flask con futura migración a FastAPI (Python).
Permite la gestión de productos, empleados, pedidos y la visualización de
métricas clave, integrando tecnologías como MySQL, Redis y Power BI para análisis avanzados.

---

## Prerrequisitos Globales

Antes de comenzar, asegúrate de tener instalado en tu sistema:

- [Git](https://git-scm.com/)
- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+ y npm](https://nodejs.org/)
- [MySQL 8+](https://dev.mysql.com/downloads/mysql/)
- [Redis](https://redis.io/download)
- (Opcional) [Power BI Desktop](https://powerbi.microsoft.com/desktop/) para visualización avanzada

---

## Clonación del Repositorio

Clona el repositorio desde GitHub:

```bash
git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo
```

---

## Configuración del Backend

### Instalación de Dependencias

1. Crea y activa un entorno virtual:

    ```bash
    python -m venv venv
    # En Windows:
    venv\Scripts\activate
    # En Linux/Mac:
    source venv/bin/activate
    ```

2. Instala las dependencias:

    ```bash
    pip install -r requirements.txt
    pip install -r dev-requirements.txt
    ```

### Configuración de la Base de Datos

1. Asegúrate de que MySQL y Redis estén en ejecución en tu máquina local.
2. Hay un ejemplo de base de datos MySQL en `db/amaluz_ddl.sql`. Puedes crear la base de datos ejecutando el script SQL proporcionado.
3. Copia el archivo `.env.example` a `.env` y configura las variables de entorno necesarias, especialmente la cadena de
   conexión a la base de datos:

    ```
    DATABASE_URL="mysql+aiomysql://usuario_velas:tu_contraseña_segura@localhost:3306/gestion_velas"
    ```
4. (Opcional) Aplica migraciones iniciales si el proyecto las incluye:

    ```bash
    alembic upgrade head
    ```

### Ejecución del Servidor Backend

Usando FastAPI (Aún en implementación). Inicia el servidor FastAPI:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Accede a la documentación interactiva de la API en: [http://localhost:8000/docs](http://localhost:8000/docs)

Usando Flask (si aún no se ha migrado a FastAPI):

```bash
cd app
flask run
---

### Ejecución de la interfaz en Tkinter

```bash
cd app
python gui.py
```

---

## Próximos Pasos (Sugerencias)

- Ejecuta migraciones de base de datos adicionales o seeders si el proyecto lo requiere.
- Configura Redis para almacenamiento en caché y sesiones si es necesario.
- Implementación del backend con FastAPI para aprovechar sus características avanzadas.

- Revisa la documentación de la aplicación en `/docs` para más detalles sobre las rutas y funcionalidades disponibles.
- Consulta los archivos de configuración y documentación adicional para personalizar el entorno según tus necesidades.

## Licencia

Este proyecto está licenciado bajo la Licencia GPL-3.0. Consulta el archivo [LICENSE](LICENSE) para más detalles.