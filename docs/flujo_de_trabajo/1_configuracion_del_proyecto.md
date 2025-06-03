# Paso 1: Configuración del Proyecto

Este documento describe los pasos necesarios para configurar el entorno de desarrollo del proyecto en tu máquina local. Seguir estos pasos te permitirá ejecutar tanto el backend como el frontend de la aplicación, así como preparar la base de datos necesaria.

## Prerrequisitos

Antes de comenzar, asegúrate de tener instaladas las siguientes herramientas en tu sistema Windows:

*   **Python**: Versión 3.11 o superior. Puedes descargarlo desde [python.org](https://www.python.org/).
    Asegúrate de marcar la opción "Add Python to PATH" durante la instalación.
*   **Node.js**: Versión 18.x o LTS (que incluye npm). Puedes descargarlo desde [nodejs.org](https://nodejs.org/).
*   **Git**: Para clonar el repositorio y gestionar versiones. Puedes descargarlo desde [git-scm.com](https://git-scm.com/).
*   **MySQL Server**: Necesitarás una instancia de MySQL en ejecución. Puedes descargar el instalador 
    de MySQL Community Server desde [dev.mysql.com](https://dev.mysql.com/downloads/mysql/).
    *   Durante la instalación, toma nota del usuario y contraseña que configures para el usuario root
        o crea un usuario específico para este proyecto.
*   **Redis**: Para la gestión de caché. Puedes descargarlo desde [redis.io](https://redis.io/download).
*   Un editor de código como IntelliJ IDEA, VS Code, etc.

## Configuración del Backend

El backend está desarrollado con FastAPI y Python.

### 1. Clonación del Repositorio

1.  Abre tu terminal o Git Bash.
2.  Navega al directorio donde deseas clonar el proyecto.
3.  Ejecuta el siguiente comando (reemplaza `<URL_DEL_REPOSITORIO>` con la URL real del repositorio Git):
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_DIRECTORIO_DEL_PROYECTO>
    ```

### 2. Crear y Activar un Entorno Virtual de Python

Es una buena práctica aislar las dependencias de tu proyecto para evitar conflictos.

#### Opción A: Usando `venv` (Recomendado para Python estándar)

En la terminal, dentro de la raíz del directorio del proyecto:

```bash
# Crear el entorno virtual (se creará una carpeta llamada .venv)
python -m venv .venv

# Activar el entorno virtual en PowerShell
.\.venv\Scripts\Activate.ps1

# O activar en el Símbolo del sistema (cmd.exe) o Git Bash
.\.venv\Scripts\activate
```
Una vez activado, verás `(.venv)` al inicio de la línea de comandos.

#### Opción B: Usando `conda` (Si utilizas Anaconda/Miniconda)

```bash
# Crear un nuevo entorno conda (puedes cambiar 'mi_entorno_proyecto' y la versión de Python)
conda create --name mi_entorno_proyecto python=3.11

# Activar el entorno conda
conda activate mi_entorno_proyecto
```
Una vez activado, verás `(mi_entorno_proyecto)` al inicio de la línea de comandos.

### 3. Instalar Dependencias del Backend

Con el entorno virtual activado, instala las dependencias listadas en los archivos `requerimientos.txt` (para producción/ejecución) y `requerimientos-dev.txt` (para desarrollo).

```bash
# Navega a la raíz del proyecto si no estás ahí
# cd <NOMBRE_DEL_DIRECTORIO_DEL_PROYECTO>

# Instalar dependencias de producción
pip install -r requerimientos.txt

# Instalar dependencias de desarrollo
pip install -r requerimientos-dev.txt
```
Esto instalará FastAPI, SQLAlchemy, Uvicorn, Alembic y todas las demás librerías necesarias para el backend.

## Configuración del Frontend

El frontend está desarrollado con React, TypeScript y Vite.

### 1. Navegar al Directorio del Frontend

Desde la raíz del proyecto, navega a la carpeta `frontend`:

```bash
cd frontend
```

### 2. Instalar Dependencias del Frontend

Usa `npm` (Node Package Manager), que viene con Node.js, para instalar las dependencias definidas en el archivo `frontend/package.json`:

```bash
npm install
```
Esto instalará React, TailwindCSS, Axios, Vite y otras librerías necesarias para el frontend. Si encuentras problemas de permisos, podrías necesitar ejecutar la terminal como administrador, aunque es preferible ajustar los permisos de la carpeta `node_modules` si es un problema recurrente.

## Configuración de la Base de Datos (MySQL)

El proyecto utiliza MySQL como sistema de gestión de bases de datos.

### 1. Asegurar que MySQL esté en Ejecución

Asegúrate de que tu servidor MySQL esté instalado y en ejecución. Durante la instalación de MySQL Server, habrás configurado un usuario (generalmente `root`) y una contraseña.

### 2. Crear la Base de Datos

Conéctate a tu servidor MySQL usando un cliente como MySQL Workbench, DBeaver, o la línea de comandos de MySQL. Crea la base de datos que utilizará la aplicación si aún no existe. El nombre de la base de datos se especificará en la configuración del backend.

```sql
CREATE DATABASE nombre_de_tu_base_de_datos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Reemplaza `nombre_de_tu_base_de_datos` con el nombre que desees (ej. `mi_proyecto_db`).

### 3. Configurar la Conexión en el Backend

El backend necesita saber cómo conectarse a la base de datos. Esto se configura típicamente mediante variables de entorno.
Crea un archivo llamado `.env` en la raíz del directorio del proyecto (al mismo nivel que `requerimientos.txt`).
Añade la siguiente línea, ajustando los valores a tu configuración de MySQL:

```env
DATABASE_URL="mysql+aiomysql://tu_usuario_mysql:tu_contraseña_mysql@localhost:3306/nombre_de_tu_base_de_datos"
# Ejemplo:
# DATABASE_URL="mysql+aiomysql://root:admin123@localhost:3306/mi_proyecto_db"
```
Asegúrate de que el usuario de MySQL tenga los permisos necesarios sobre la base de datos creada.

### 4. Aplicar Migraciones de Base de Datos

El proyecto utiliza Alembic para gestionar las migraciones del esquema de la base de datos (crear tablas, modificarlas, etc.). Con el entorno virtual del backend activado y desde la raíz del proyecto:

```bash
# Asegúrate de estar en la raíz del proyecto y con el entorno virtual del backend activado
alembic upgrade head
```
Esto ejecutará los scripts de migración para crear todas las tablas y estructuras necesarias en tu base de datos, basándose en los modelos de SQLAlchemy definidos en el proyecto.

## Verificación de la Configuración

Una vez completados todos los pasos, puedes verificar si la configuración es correcta ejecutando las aplicaciones.

### 1. Ejecutar el Backend

Desde la raíz del proyecto, con el entorno virtual del backend activado:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Abre tu navegador y ve a `http://localhost:8000/docs`. Deberías ver la interfaz de documentación interactiva de la API de FastAPI.

### 2. Ejecutar el Frontend

Abre una **nueva terminal**. Navega al directorio `frontend` y ejecuta:

```bash
# cd frontend (si no estás ya en el directorio)
npm run dev
```