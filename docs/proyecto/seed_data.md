## Documentación del Script `seed_data.py`

### Introducción

El script `seed_data.py` es el orquestador principal para poblar la base de datos de la aplicación con datos de prueba.
Su función es simular un entorno realista con usuarios, proveedores, productos, inventario, descuentos, carritos y
pedidos, lo cual es esencial para el desarrollo, pruebas y demostración de la aplicación. Ejecuta una secuencia de
operaciones para asegurar que los datos generados sean coherentes y respeten las interdependencias entre las diferentes
entidades del sistema.

### Funcionamiento Principal

La lógica central del script reside en la función `main()`. Esta función establece una conexión con la base de datos y
luego invoca secuencialmente a diferentes módulos y funciones encargadas de generar datos para cada entidad específica.

### Constantes de Generación

Al inicio del script, se definen varias constantes que controlan el volumen de datos a generar:

* `USUARIOS_COUNT`: Define el número total de usuarios a crear.
* `PROVEEDORES_COUNT`: Especifica cuántos proveedores se generarán.
* `PRODUCTOS_COUNT`: Determina el número de productos a crear en el catálogo.
* `PEDIDOS_COUNT`: Define la cantidad de pedidos que se simularán.

Estas constantes permiten ajustar fácilmente la cantidad de datos de prueba según las necesidades (por ejemplo, pruebas
rápidas con pocos datos o pruebas de carga con un volumen mayor).

### Orquestación de la Generación de Datos

La función `main()` sigue un orden específico para la creación de datos, respetando las dependencias entre entidades:

1. **Configuración de Logging:** Se inicializa el sistema de logging para registrar el progreso y los posibles errores
   durante la ejecución.
2. **Conexión a la Base de Datos:** Se obtiene una sesión de base de datos síncrona utilizando `get_sync_db()`.
3. **Creación de Usuarios (`create_users`):** Se generan los usuarios iniciales.
4. **Actualización de Estado de Usuarios (`update_user_estado`):** Se actualiza el estado de algunos usuarios (por
   ejemplo, de 'Sin confirmar' a 'Activo') para simular el flujo de confirmación de cuentas.
5. **Obtención de Clientes Activos (`get_usuarios_activos_clientes`):** Se recupera una lista de usuarios que son
   clientes y están activos, ya que estos serán los que realicen acciones como crear carritos y pedidos.
6. **Creación de Proveedores (`create_proveedores`):** Se generan los proveedores de productos.
7. **Creación de Productos (`create_productos`):** Se crean los productos, asociándolos a los proveedores previamente
   generados.
8. **Creación de Inventario Inicial (`create_inventario_inicial`):** Se establece un stock inicial para cada producto.
9. **Creación de Descuentos (`create_descuentos`):** Se generan diversos tipos de descuentos que podrán ser aplicados a
   los pedidos.
10. **Creación de Carritos (`create_carrito`):** Se simula la creación de carritos de compra por parte de los clientes
    activos, añadiendo productos a ellos. El número de carritos se calcula dinámicamente basado en el número de clientes
    activos.
11. **Creación de Pedidos (`create_pedidos`):** Se generan los pedidos, utilizando la información de los carritos y
    aplicando descuentos de forma aleatoria.

### Manejo de Errores

El script incluye un bloque `try-except` general dentro de la función `main()` para capturar y manejar excepciones
durante el proceso de generación de datos:

* `IntegrityError`: Captura errores específicos de la base de datos relacionados con violaciones de restricciones de
  integridad (por ejemplo, claves únicas duplicadas). En caso de ocurrir, se realiza un `db.rollback()` para deshacer la
  transacción actual y se registra el error.
* `Exception`: Captura cualquier otro error inesperado. También realiza un `db.rollback()` y registra los detalles del
  error.

Este manejo de errores asegura que, en caso de fallo, la base de datos no quede en un estado inconsistente y se
proporcione información útil para diagnosticar el problema.

### Ejecución del Script

Para poblar la base de datos, el script se ejecuta directamente desde la línea de comandos:

```bash
python seed_data.py
```

Esto iniciará el proceso de generación de datos, mostrando mensajes de log en la consola sobre el progreso y los
resultados de cada etapa.

---

### Documentación del archivo `usuarios.py`

---

### Introducción

El archivo `usuarios.py` es un módulo encargado de la generación de datos de prueba relacionados con los usuarios en la base de datos. Proporciona funciones para crear usuarios, actualizar su estado y obtener listas de usuarios activos que son clientes. Este módulo utiliza herramientas como `Faker` para generar datos ficticios y asegura la coherencia temporal y unicidad de los datos generados.

---

### Funciones principales

#### `create_users(db: Session, count: int)`
**Descripción:**  
Genera una lista de usuarios ficticios y los inserta en la base de datos. Los usuarios pueden ser administradores, vendedores o clientes, con atributos como nombre, correo, teléfono, género, fecha de nacimiento y estado.

**Parámetros:**
- `db`: Sesión de base de datos.
- `count`: Número de usuarios a crear.

**Retorno:**  
Lista de objetos `Usuario` creados.

**Detalles:**
- Utiliza `Faker` para generar datos ficticios como nombres, correos y teléfonos.
- Asegura unicidad en correos y teléfonos.
- Establece fechas de registro secuenciales según el tipo de usuario.
- Incluye lógica específica para administradores y vendedores.

---

#### `update_user_estado(db: Session, num_sin_confirmar_a_dejar: int = 20)`
**Descripción:**  
Actualiza el estado de los usuarios de "Sin confirmar" a "Activo", dejando un número específico de usuarios en estado "Sin confirmar".

**Parámetros:**
- `db`: Sesión de base de datos.
- `num_sin_confirmar_a_dejar`: Número de usuarios que deben permanecer en estado "Sin confirmar".

**Retorno:**  
No retorna valores.

**Detalles:**
- Selecciona aleatoriamente usuarios para actualizar su estado.
- Simula tiempos de confirmación de cuentas (rápido o tardío).
- Actualiza la fecha de modificación (`fecha_actualizacion`) de los usuarios modificados.

---

#### `get_usuarios_activos_clientes(db: Session)`
**Descripción:**  
Obtiene una lista de usuarios que son clientes y tienen estado "Activo".

**Parámetros:**
- `db`: Sesión de base de datos.

**Retorno:**  
Lista de usuarios activos que son clientes.

**Detalles:**
- Filtra usuarios por tipo (`Cliente`) y estado (`Activo`).

---

### Configuración y dependencias

- **Librerías utilizadas:**
    - `Faker`: Para generar datos ficticios como nombres, correos y teléfonos.
    - `logging`: Para registrar información sobre el proceso de generación y actualización.
    - `datetime`: Para manejar fechas y tiempos.
    - `sqlalchemy.orm.Session`: Para interactuar con la base de datos.

- **Dependencias internas:**
    - `sanear_string_para_correo` y `generar_fecha_secuencial` de `utils` y `utils_datetime`.
    - Modelos como `Usuario`, `EstadoUsuarioEnum`, `TipoUsuarioEnum` y `GeneroEnum`.

---

### Advertencias

- **Unicidad:**  
  Asegúrate de que los correos y teléfonos generados sean únicos para evitar errores de integridad en la base de datos.

- **Coherencia temporal:**  
  Las fechas de registro y actualización deben ser consistentes y respetar las reglas de negocio.

- **Manejo de errores:**  
  Implementa bloques `try-except` para capturar y manejar excepciones durante las operaciones de base de datos.

--- 

### Ejemplo de uso

```python
from sqlalchemy.orm import Session
from app.db.data_generation.usuarios import create_users, update_user_estado, get_usuarios_activos_clientes

# Crear usuarios
usuarios = create_users(db=session, count=100)

# Actualizar estado de usuarios
update_user_estado(db=session, num_sin_confirmar_a_dejar=10)

# Obtener clientes activos
clientes_activos = get_usuarios_activos_clientes(db=session)
```
---

### Documentación del archivo `proveedores.py`

---

### Introducción

El archivo `proveedores.py` es un módulo encargado de la generación de datos de prueba relacionados con los proveedores en la base de datos. Proporciona funciones para crear proveedores con atributos ficticios como nombre, teléfono, dirección y fechas de registro. Este módulo asegura la coherencia temporal y utiliza la librería `Faker` para generar datos realistas.

---

### Funciones principales

#### `create_proveedores(db: Session, count: int)`

**Descripción:**  
Genera una lista de proveedores ficticios y los inserta en la base de datos. Cada proveedor tiene atributos como nombre, teléfono, dirección y fechas de registro y actualización.

**Parámetros:**
- `db`: Sesión de base de datos.
- `count`: Número de proveedores a crear.

**Retorno:**  
Lista de objetos `Proveedor` creados.

**Detalles:**
- Utiliza `Faker` para generar datos ficticios como nombres de empresas, teléfonos y direcciones.
- Las fechas de registro se distribuyen secuencialmente entre un rango definido (`PROVEEDORES_START_DATE_LIMIT` y `PROVEEDORES_END_DATE_LIMIT`).
- Asegura que las fechas de registro no excedan el límite superior.
- Inicialmente, la fecha de actualización es igual a la fecha de registro.

---

### Configuración y dependencias

- **Librerías utilizadas:**
    - `Faker`: Para generar datos ficticios como nombres de empresas, teléfonos y direcciones.
    - `logging`: Para registrar información sobre el proceso de generación.
    - `datetime`: Para manejar fechas y tiempos.
    - `sqlalchemy.orm.Session`: Para interactuar con la base de datos.

- **Dependencias internas:**
    - Modelo `Proveedor`.

---

### Advertencias

- **Coherencia temporal:**  
  Las fechas de registro deben respetar el rango definido y ser consistentes con las reglas de negocio.

- **Manejo de errores:**  
  Implementa bloques `try-except` en el código que utiliza esta función para capturar y manejar excepciones durante las operaciones de base de datos.

---

### Ejemplo de uso

```python
from sqlalchemy.orm import Session
from app.db.data_generation.proveedores import create_proveedores

# Crear proveedores
proveedores = create_proveedores(db=session, count=50)
```
---

### Documentación del archivo `productos.py`

---

### Introducción

El archivo `productos.py` es un módulo encargado de la generación de datos de prueba relacionados con los productos en la base de datos. Proporciona funciones para crear productos asociados a proveedores, asegurando coherencia temporal y respetando las reglas de negocio. Este módulo utiliza herramientas como `Faker` y generadores de IA para crear datos realistas.

---

### Funciones principales

#### `create_productos(db: Session, count: int, proveedores: list[Proveedor])`

**Descripción:**  
Genera una lista de productos ficticios y los inserta en la base de datos. Cada producto se asocia a un proveedor existente y tiene atributos como nombre, descripción, precio, dimensiones, fragancia, categoría y fechas de registro y actualización.

**Parámetros:**
- `db`: Sesión de base de datos.
- `count`: Número de productos a crear.
- `proveedores`: Lista de proveedores disponibles para asociar con los productos.

**Retorno:**  
Lista de objetos `Producto` creados.

**Detalles:**
- Distribuye los productos entre los proveedores de forma proporcional, considerando la antigüedad de registro de cada proveedor.
- Genera nombres y descripciones utilizando IA o datos ficticios en caso de error.
- Asegura que las fechas de registro de los productos sean posteriores a las de sus proveedores.
- Calcula precios de venta basados en el precio del proveedor con incrementos aleatorios.
- Genera dimensiones y peso realistas según el tamaño del producto.
- Utiliza herramientas como `Pollinations` para generar imágenes de productos.

---

### Configuración y dependencias

- **Librerías utilizadas:**
    - `Faker`: Para generar datos ficticios como nombres y descripciones.
    - `logging`: Para registrar información sobre el proceso de generación.
    - `datetime`: Para manejar fechas y tiempos.
    - `decimal`: Para manejar precios y pesos.
    - `sqlalchemy.orm.Session`: Para interactuar con la base de datos.
    - `sqlalchemy.exc.SQLAlchemyError`: Para manejar errores de base de datos.

- **Dependencias internas:**
    - Modelos como `Producto`, `Proveedor`, `CategoriaProductoEnum`, `EstadoProductoEnum` y `FraganciaProductoEnum`.
    - Generadores de IA como `generar_nombre_producto_ia`, `generar_descripcion_producto_ia` y `generate_image_pollinations`.
    - Utilidades como `PRODUCTOS_START_DATE_LIMIT` y `PRODUCTOS_END_DATE_LIMIT` de `utils_datetime`.

---

### Advertencias

- **Coherencia temporal:**  
  Las fechas de registro de los productos deben ser posteriores a las de sus proveedores y respetar los límites definidos.

- **Manejo de errores:**  
  Implementa bloques `try-except` para capturar y manejar excepciones durante las operaciones de base de datos y generación de datos.

- **Distribución proporcional:**  
  Asegúrate de que la lógica de distribución de productos entre proveedores sea consistente y respete las reglas de negocio.

---

### Ejemplo de uso

```python
from sqlalchemy.orm import Session
from app.db.data_generation.productos import create_productos
from app.models.proveedor import Proveedor

# Crear productos
proveedores = [...]  # Lista de proveedores obtenida previamente
productos = create_productos(db=session, count=100, proveedores=proveedores)
```
---

### Documentación del archivo `inventario.py`

---

### Introducción

El archivo `inventario.py` es un módulo crucial para la simulación de la gestión de stock en la base de datos. Proporciona funcionalidades para crear el inventario inicial de los productos, actualizar las cantidades disponibles tras la creación de pedidos o cancelaciones, y gestionar la reposición de stock basada en la popularidad de los productos y umbrales definidos. Este módulo interactúa estrechamente con los productos, pedidos y detalles de pedidos para mantener la coherencia de los datos de inventario.

---

### Funciones principales

#### `determinar_cantidad_reposicion(nivel_popularidad: int, ranking_en_categoria: int) -> int`
**Descripción:**  
Determina la cantidad de unidades a reponer para un producto basándose en su nivel de popularidad y su ranking dentro de esa categoría de popularidad.

**Parámetros:**
- `nivel_popularidad`: Nivel de popularidad del producto (escala 0-10).
- `ranking_en_categoria`: Posición del producto dentro de su categoría de popularidad (ej. 1 para el más popular).

**Retorno:**  
Cantidad de unidades a reponer.

**Detalles:**
- Define diferentes cantidades de reposición para productos populares, medios y poco populares, ajustando la cantidad según el ranking específico del producto.

---

#### `calcular_cantidad_reposicion(db: Session, producto_id: int) -> int`
**Descripción:**  
Calcula la cantidad de reposición para un producto específico. Primero determina la popularidad de todos los productos activos, los clasifica y luego usa `determinar_cantidad_reposicion` para obtener la cantidad a reponer para el producto dado.

**Parámetros:**
- `db`: Sesión de base de datos.
- `producto_id`: ID del producto para el cual se calcula la reposición.

**Retorno:**  
Cantidad de unidades a reponer.

**Detalles:**
- Obtiene todos los productos activos.
- Calcula la popularidad de cada uno usando `calcular_popularidad`.
- Agrupa los productos en categorías de popularidad (populares, medios, poco populares) y los ordena.
- Determina el ranking del producto específico dentro de su categoría.
- Llama a `determinar_cantidad_reposicion` con la popularidad y ranking obtenidos.

---

#### `calcular_popularidad(db: Session, producto_id: int) -> Decimal`
**Descripción:**  
Calcula el nivel de popularidad de un producto en una escala de 0 a 10. Esta popularidad se basa en la cantidad de ventas, el número de comentarios positivos y las veces que ha sido añadido a carritos.

**Parámetros:**
- `db`: Sesión de base de datos.
- `producto_id`: ID del producto.

**Retorno:**  
Nivel de popularidad del producto (Decimal entre 0 y 10).

**Detalles:**
- Contabiliza ventas de pedidos entregados, comentarios con calificación >= 4 y cantidad de veces en carritos.
- Normaliza estos valores con respecto a los máximos observados en la base de datos.
- Aplica pesos configurables a cada factor (ventas, comentarios, carritos) para calcular una puntuación ponderada.

---

#### `create_inventario_inicial(db: Session, productos: list[Producto]) -> list[Inventario]`
**Descripción:**  
Crea los registros de inventario inicial para una lista de productos. Establece una cantidad inicial y asegura que la fecha de registro del inventario sea coherente con la fecha de registro del producto.

**Parámetros:**
- `db`: Sesión de base de datos.
- `productos`: Lista de objetos `Producto` para los cuales se creará el inventario.

**Retorno:**  
Lista de objetos `Inventario` creados.

**Detalles:**
- Para cada producto, la fecha de registro del inventario se genera aleatoriamente en un breve intervalo posterior a la fecha de registro del producto.
- La cantidad inicial por defecto es 24 unidades.
- La `fecha_actualizacion` inicial del inventario se establece igual a su `fecha_registro`.

---

#### `actualizar_inventario_por_pedido(db: Session, detalle_pedido: DetallePedido, fecha_operacion: datetime) -> Tuple[bool, Optional[Inventario]]`
**Descripción:**  
Actualiza el inventario cuando se procesa un detalle de pedido (generalmente al crear un pedido). Decrementa la cantidad disponible y en mano. Si el stock llega a cero, el producto puede marcarse como inactivo. También verifica si es necesario reponer el inventario.

**Parámetros:**
- `db`: Sesión de base de datos.
- `detalle_pedido`: Objeto `DetallePedido` que contiene el producto y la cantidad vendida.
- `fecha_operacion`: Fecha y hora en que se realiza la actualización del inventario.

**Retorno:**  
Una tupla `(bool, Optional[Inventario])` donde el booleano indica si la operación fue exitosa y el segundo elemento es el objeto `Inventario` actualizado (o `None` en caso de error).

**Detalles:**
- Verifica si hay stock suficiente antes de decrementar.
- Si `cantidad_disponible` llega a 0, el estado del `Producto` asociado se cambia a `Inactivo`.
- Llama a `verificar_reposicion_inventario` para gestionar posibles reposiciones.

---

#### `verificar_reposicion_inventario(db: Session, inventario: Inventario, fecha_operacion: datetime) -> bool`
**Descripción:**  
Verifica si el inventario de un producto ha caído por debajo del umbral de reposición (`UMBRAL_REPOSICION`). Si es así y ha pasado suficiente tiempo desde la última reposición (`PERIODO_MINIMO_REPOSICION`), calcula la cantidad a reponer y actualiza el inventario.

**Parámetros:**
- `db`: Sesión de base de datos.
- `inventario`: Objeto `Inventario` del producto a verificar.
- `fecha_operacion`: Fecha y hora de la operación que podría disparar la reposición.

**Retorno:**  
`True` si se realizó una reposición, `False` en caso contrario.

**Detalles:**
- Utiliza `calcular_cantidad_reposicion` para determinar cuántas unidades reponer.
- La fecha de reposición se programa para unos días después de `fecha_operacion`.
- Actualiza `cantidad_disponible` y `cantidad_mano`.
- Si el producto estaba inactivo, lo reactiva.
- Registra la fecha de la última reposición para evitar reposiciones demasiado frecuentes.

---

#### `validar_disponibilidad_producto(db: Session, producto_id: int, cantidad_requerida: int) -> bool`
**Descripción:**  
Comprueba si un producto específico está activo y si hay suficiente cantidad disponible en el inventario para satisfacer una cantidad requerida.

**Parámetros:**
- `db`: Sesión de base de datos.
- `producto_id`: ID del producto a verificar.
- `cantidad_requerida`: Cantidad que se desea comprobar.

**Retorno:**  
`True` si el producto está activo y hay suficiente stock, `False` en caso contrario.

---

#### `reponer_stock_tras_cancelacion(db: Session, producto_id: int, cantidad_repuesta: int, fecha_operacion: datetime) -> Tuple[bool, Optional[Inventario]]`
**Descripción:**  
Incrementa el stock de un producto cuando un ítem de pedido es cancelado. Aumenta `cantidad_disponible` y `cantidad_mano`. Si el producto estaba inactivo debido a falta de stock, lo reactiva.

**Parámetros:**
- `db`: Sesión de base de datos.
- `producto_id`: ID del producto cuyo stock se va a reponer.
- `cantidad_repuesta`: Cantidad de unidades a devolver al inventario.
- `fecha_operacion`: Fecha y hora de la operación de cancelación.

**Retorno:**  
Una tupla `(bool, Optional[Inventario])` donde el booleano indica si la operación fue exitosa y el segundo elemento es el objeto `Inventario` actualizado.

**Detalles:**
- Si el producto estaba `Inactivo` y la reposición hace que `cantidad_disponible` sea mayor que cero, el producto se reactiva.
- La `fecha_actualizacion` del inventario se establece a `fecha_operacion`.

---

#### `obtener_cantidad_disponible(db: Session, producto_id: int) -> int`
**Descripción:**  
Obtiene la cantidad disponible actual de un producto específico según su registro de inventario.

**Parámetros:**
- `db`: Sesión de base de datos.
- `producto_id`: ID del producto.

**Retorno:**  
La cantidad disponible del producto, o 0 si el producto no tiene inventario o no se encuentra.

---

### Constantes y Variables Globales Clave

- `PRODUCTOS_END_DATE_LIMIT`: Límite superior de fecha para operaciones relacionadas con productos/inventario.
- `UMBRAL_REPOSICION`: Cantidad mínima de stock a partir de la cual se considera una reposición.
- `PERIODO_MINIMO_REPOSICION`: Número mínimo de días que deben pasar entre reposiciones de un mismo producto.
- `ultimas_reposiciones`: Diccionario en memoria para rastrear la fecha de la última reposición de cada producto y evitar reposiciones demasiado frecuentes dentro de una misma ejecución del script de poblado.

---

### Configuración y dependencias

- **Librerías utilizadas:**
    - `random`: Para generar valores aleatorios (ej. días para reposición).
    - `logging`: Para registrar el progreso y los errores.
    - `decimal.Decimal`: Para manejar cantidades monetarias o de precisión.
    - `typing.Tuple`, `typing.Optional`: Para anotaciones de tipo.
    - `collections.defaultdict`: Usado internamente (aunque `VENTAS_POR_PRODUCTO` no se usa directamente en las funciones exportadas).
    - `datetime`, `timedelta`: Para manipulación de fechas y tiempos.
    - `sqlalchemy.orm.Session`, `sqlalchemy.func`, `sqlalchemy.exc.SQLAlchemyError`: Para interacción con la base de datos y manejo de errores SQL.
    - `Faker`: Para generación de datos ficticios (aunque `fkr` no se usa directamente en las funciones exportadas de este módulo).

- **Dependencias internas:**
    - `app.db.data_generation.utils_datetime.get_random_datetime_in_range`: Para generar fechas aleatorias dentro de un rango.
    - Modelos de `app.models`: `Producto`, `Inventario`, `Pedido`, `DetallePedido`, `Comentario`, `Carrito`.
    - Enums: `EstadoProductoEnum`, `EstadoPedidoEnum`.

---

### Advertencias

- **Coherencia Temporal:** Es fundamental que las fechas de las operaciones de inventario (`fecha_registro`, `fecha_actualizacion`) sean consistentes con las fechas de los eventos que las desencadenan (creación de producto, creación de pedido, cancelación, etc.). El módulo intenta gestionar esto, por ejemplo, asegurando que la `fecha_actualizacion` siempre avance.
- **Gestión de Transacciones:** Las funciones que modifican la base de datos (crear, actualizar inventario) realizan `db.flush()` para persistir cambios en la sesión actual, pero generalmente esperan que la función que las llama maneje el `db.commit()` o `db.rollback()` final para asegurar la atomicidad de operaciones más grandes.
- **Lógica de Popularidad y Reposición:** Los cálculos de popularidad y las reglas de reposición (umbrales, cantidades, periodos) son específicos de esta simulación y pueden necesitar ajustes según los objetivos del análisis de datos.
- **Estado en Memoria (`ultimas_reposiciones`):** El diccionario `ultimas_reposiciones` mantiene estado en memoria durante la ejecución del script. Esto significa que su conocimiento sobre las últimas reposiciones se reinicia cada vez que el script `seed_data.py` se ejecuta.

---

### Ejemplo de uso

```python
from sqlalchemy.orm import Session
from app.models.producto import Producto
from app.models.detalle_pedido import DetallePedido
from app.db.data_generation.inventario import (
    create_inventario_inicial,
    actualizar_inventario_por_pedido,
    reponer_stock_tras_cancelacion
)
from datetime import datetime

# Asumiendo que 'session' es una instancia de SQLAlchemy Session
# y 'lista_de_productos' es una lista de objetos Producto

# 1. Crear inventario inicial para los productos
inventarios_creados = create_inventario_inicial(db=session, productos=lista_de_productos)

# 2. Actualizar inventario después de crear un detalle de pedido
# Asumiendo que 'un_detalle_pedido' es un objeto DetallePedido
fecha_actual = datetime.now()
exito, inv_actualizado = actualizar_inventario_por_pedido(
    db=session,
    detalle_pedido=un_detalle_pedido,
    fecha_operacion=fecha_actual
)
if exito:
    print(f"Inventario actualizado para producto {un_detalle_pedido.producto_id}")

# 3. Reponer stock tras una cancelación
producto_id_cancelado = 10
cantidad_cancelada = 2
fecha_cancelacion = datetime.now()
exito_repo, inv_repuesto = reponer_stock_tras_cancelacion(
    db=session,
    producto_id=producto_id_cancelado,
    cantidad_repuesta=cantidad_cancelada,
    fecha_operacion=fecha_cancelacion
)
if exito_repo:
    print(f"Stock repuesto para producto {producto_id_cancelado}")

# Es importante hacer commit de la sesión después de estas operaciones si son exitosas
# session.commit()
```
---

### Documentación del archivo `descuentos.py`

---

### Introducción

El archivo `descuentos.py` es un módulo dedicado a la generación de datos de prueba para la entidad `Descuento` en la base de datos. Proporciona la funcionalidad para crear una variedad de descuentos, tanto asociados a fechas especiales predefinidas como descuentos generados de forma más aleatoria, asegurando la coherencia temporal y la validez de los datos dentro del marco de la simulación.

---

### Funciones principales

#### `create_descuentos(db: Session) -> List[Descuento]`
**Descripción:**  
Genera una lista de objetos `Descuento` y los persiste en la base de datos. Los descuentos se crean basados en un conjunto de fechas especiales predefinidas (almacenadas en `FECHAS_DESCUENTOS`) y también se pueden generar descuentos adicionales de forma aleatoria si no se alcanzan ciertos umbrales o para cubrir periodos no contemplados por las fechas especiales.

**Parámetros:**
- `db`: Sesión de base de datos SQLAlchemy.

**Retorno:**  
Una lista de los objetos `Descuento` que fueron creados y guardados en la base de datos.

**Detalles:**
- Itera sobre el diccionario `FECHAS_DESCUENTOS` para crear descuentos temáticos.
- Para cada descuento, genera un código único (ej. `SANVALENTIN2022_XYZ`).
- El porcentaje de descuento se elige aleatoriamente entre `MIN_DISCOUNT_PERCENTAGE` y `MAX_DISCOUNT_PERCENTAGE`.
- La duración del descuento se determina aleatoriamente entre `MIN_DISCOUNT_DURATION_DAYS` y `MAX_DISCOUNT_DURATION_DAYS`.
- La fecha de inicio del descuento se basa en la fecha especial, con una ligera variación aleatoria.
- La fecha de fin se calcula sumando la duración a la fecha de inicio.
- La fecha de registro del descuento se genera aleatoriamente en un periodo anterior a la fecha de inicio del descuento, hasta `MAX_DAYS_BEFORE_START_FOR_REGISTRATION` días antes.
- Se asegura que todas las fechas generadas (registro, inicio, fin) estén dentro de los límites de la simulación (`SIMULATION_START_DATE` y `SIMULATION_END_DATE`).
- El estado inicial de los descuentos es `Activo`.
- Maneja posibles errores durante la inserción en la base de datos.

---

### Constantes y Variables Globales Clave

- `SIMULATION_START_DATE`: Fecha de inicio global para la generación de datos de simulación (ej. `datetime(2022, 2, 1)`).
- `SIMULATION_END_DATE`: Fecha de fin global para la generación de datos de simulación (ej. `datetime(2025, 5, 1)`).
- `MIN_DISCOUNT_PERCENTAGE`: Porcentaje mínimo que puede tener un descuento (ej. 10%).
- `MAX_DISCOUNT_PERCENTAGE`: Porcentaje máximo que puede tener un descuento (ej. 50%).
- `MIN_DISCOUNT_DURATION_DAYS`: Duración mínima en días para un descuento (ej. 3 días).
- `MAX_DISCOUNT_DURATION_DAYS`: Duración máxima en días para un descuento (ej. 7 días).
- `MAX_DAYS_BEFORE_START_FOR_REGISTRATION`: Número máximo de días antes de la fecha de inicio de un descuento en que este puede ser registrado en el sistema (ej. 30 días).
- `FECHAS_DESCUENTOS`: Un diccionario que mapea nombres de eventos o campañas de descuento (ej. `"san_valentin_2022"`) a sus fechas centrales (`datetime`). Este diccionario es la base para generar descuentos temáticos.

---

### Configuración y dependencias

- **Librerías utilizadas:**
    - `logging`: Para el registro de información y errores.
    - `random`: Para la generación de números aleatorios, selección de elementos y generación de partes de códigos.
    - `string`: Utilizado para generar caracteres aleatorios para los códigos de descuento.
    - `datetime`, `timedelta`: Para la manipulación de fechas y cálculos de duración.
    - `typing.List`, `typing.Optional`: Para anotaciones de tipo.
    - `Faker`: Para la generación de datos ficticios (aunque en el fragmento actual `fake` se inicializa pero no se usa directamente en `create_descuentos`).
    - `sqlalchemy.orm.Session`: Para la interacción con la base de datos.
    - `sqlalchemy.exc.SQLAlchemyError`: Para el manejo de excepciones de SQLAlchemy.

- **Dependencias internas:**
    - `app.models.descuento.Descuento`: El modelo SQLAlchemy para la tabla de descuentos.
    - `app.models.descuento.EstadoDescuentoEnum`: Enum para los posibles estados de un descuento.
    - `app.db.data_generation.utils_datetime.get_random_datetime_in_range`: Función de utilidad para obtener una fecha y hora aleatoria dentro de un rango específico.

---

### Advertencias

- **Coherencia Temporal:** Es crucial que las fechas de registro, inicio y fin de los descuentos sean lógicamente consistentes entre sí y con los límites globales de la simulación. El módulo intenta manejar esto, pero la configuración de las constantes es vital.
- **Unicidad de Códigos:** La generación de códigos de descuento intenta asegurar la unicidad añadiendo caracteres aleatorios. Sin embargo, en escenarios de generación masiva, se debería considerar una estrategia de verificación de unicidad más robusta si fuera necesario, aunque el riesgo es bajo con la combinación de nombre de evento, año y sufijo aleatorio.
- **Volumen de Descuentos:** El número de descuentos generados depende directamente del tamaño del diccionario `FECHAS_DESCUENTOS` y de cualquier lógica adicional para generar descuentos aleatorios no mostrada en el extracto.
- **Manejo de Errores:** La función `create_descuentos` incluye un bloque `try-except` para `SQLAlchemyError`, lo que permite capturar errores durante la interacción con la base de datos y realizar un `rollback`.

---

### Ejemplo de uso

```python
from sqlalchemy.orm import Session
from app.db.database import SessionLocal # o tu forma de obtener la sesión
from app.db.data_generation.descuentos import create_descuentos

# Obtener una sesión de base de datos
db: Session = SessionLocal()

try:
    # Crear descuentos
    lista_descuentos_creados = create_descuentos(db=db)
    logger.info(f"Se crearon {len(lista_descuentos_creados)} descuentos.")
    # Aquí se podría hacer db.commit() si create_descuentos no lo hace internamente
    # o si es parte de una transacción mayor.
    # Asumiendo que create_descuentos hace commit por cada descuento o al final:
    # db.commit() # Descomentar si es necesario
except Exception as e:
    logger.error(f"Error al crear descuentos: {e}")
    db.rollback()
finally:
    db.close()
```
---

### Documentación del archivo `carrito.py`

---

### Introducción

El archivo `carrito.py` es un módulo diseñado para la generación de datos de prueba relacionados con los carritos de compra de los usuarios. Su función principal es simular la acción de añadir productos a un carrito, creando los registros correspondientes en la base de datos. Este módulo tiene en cuenta la disponibilidad de stock de los productos y la coherencia temporal de las acciones.

---

### Funciones principales

#### `create_carrito(db: Session, count: int, usuarios: list[Usuario], productos: list[Producto]) -> list[Carrito]`
**Descripción:**  
Genera una cantidad específica de ítems de carrito, asociándolos aleatoriamente a usuarios activos y productos disponibles. Persiste estos ítems en la base de datos.

**Parámetros:**
- `db`: Sesión de base de datos SQLAlchemy.
- `count`: Número total de ítems de carrito a crear.
- `usuarios`: Lista de objetos `Usuario` (clientes activos) que pueden tener carritos.
- `productos`: Lista de objetos `Producto` que pueden ser añadidos a los carritos.

**Retorno:**  
Una lista de los objetos `Carrito` (ítems de carrito) que fueron creados y guardados en la base de datos.

**Detalles:**
- Selecciona aleatoriamente un usuario y un producto para cada ítem de carrito.
- Genera una cantidad aleatoria para el producto en el carrito (generalmente entre 1 y 3 unidades).
- Verifica la disponibilidad de stock del producto utilizando `obtener_cantidad_disponible` antes de añadirlo al carrito. Si no hay stock suficiente, se omite la creación de ese ítem de carrito específico o se intenta con otro producto/usuario.
- La fecha de creación (`fecha_creacion`) y la fecha de última actualización (`fecha_actualizacion`) del ítem de carrito se generan aleatoriamente dentro del rango de simulación (`SIMULATION_START_DATE` y `SIMULATION_END_DATE`), asegurando que la fecha de creación del carrito sea posterior a la fecha de registro del producto y del usuario.
- Se intenta distribuir la creación de carritos a lo largo del periodo de simulación.
- Maneja posibles errores durante la interacción con la base de datos.

---

### Constantes y Variables Globales Clave

- `SIMULATION_START_DATE`: Fecha y hora de inicio para el periodo de simulación dentro del cual se pueden crear los carritos (ej. `datetime(2022, 1, 15, 0, 0, 0)`).
- `SIMULATION_END_DATE`: Fecha y hora de fin para el periodo de simulación (ej. `datetime(2025, 5, 10, 23, 59, 59)`).
- `logger`: Instancia del logger para registrar información y errores durante la generación de datos.

---

### Configuración y dependencias

- **Librerías utilizadas:**
    - `logging`: Para el registro de información y errores.
    - `random`: Para la selección aleatoria de usuarios, productos y cantidades, así como para la generación de fechas.
    - `datetime`, `timedelta`: Para la manipulación de fechas y tiempos.
    - `sqlalchemy.orm.Session`: Para la interacción con la base de datos.
    - `sqlalchemy.exc.SQLAlchemyError`: Para el manejo de excepciones de SQLAlchemy.

- **Dependencias internas:**
    - `app.models.usuario.Usuario`: El modelo SQLAlchemy para la tabla de usuarios.
    - `app.models.producto.Producto`: El modelo SQLAlchemy para la tabla de productos.
    - `app.models.carrito.Carrito`: El modelo SQLAlchemy para la tabla de carritos.
    - `app.db.data_generation.inventario.obtener_cantidad_disponible`: Función para verificar el stock de un producto.

---

### Advertencias

- **Coherencia Temporal:** Es fundamental que la `fecha_creacion` de los ítems de carrito sea lógicamente consistente con las fechas de registro de los usuarios y productos asociados, y que esté dentro del rango de simulación.
- **Disponibilidad de Stock:** La lógica debe asegurar que solo se añadan al carrito productos con stock disponible. Si un producto se queda sin stock, no debería poder añadirse.
- **Volumen de Datos:** El parámetro `count` determina cuántos ítems de carrito se intentarán crear. Un número muy alto podría llevar a tiempos de ejecución prolongados.
- **Manejo de Errores:** La función `create_carrito` debe incluir manejo de excepciones (ej. `SQLAlchemyError`) para asegurar que los errores durante la inserción en la base de datos sean capturados y gestionados, posiblemente con un `rollback`.

---

### Ejemplo de uso

```python
from sqlalchemy.orm import Session
from app.db.database import SessionLocal # o tu forma de obtener la sesión
from app.db.data_generation.carrito import create_carrito
# Asumimos que ya hemos obtenido listas de usuarios y productos
# from app.db.data_generation.usuarios import get_usuarios_activos_clientes
# from app.db.data_generation.productos import create_productos (o una función para obtenerlos)

# Obtener una sesión de base de datos
db: Session = SessionLocal()

try:
    # Obtener usuarios activos y productos (ejemplos)
    # usuarios_activos = get_usuarios_activos_clientes(db)
    # lista_productos = obtener_todos_los_productos(db) # Función hipotética
    
    # Estas listas deberían ser obtenidas de llamadas previas en el script de seed_data
    usuarios_para_carritos = [...] 
    productos_para_carritos = [...]
    numero_de_items_carrito = 500

    # Crear ítems de carrito
    items_carrito_creados = create_carrito(
        db=db,
        count=numero_de_items_carrito,
        usuarios=usuarios_para_carritos,
        productos=productos_para_carritos
    )
    logger.info(f"Se crearon {len(items_carrito_creados)} ítems de carrito.")
    
    # Generalmente, el commit se maneja en el script principal (seed_data.py)
    # db.commit()
except Exception as e:
    logger.error(f"Error al crear ítems de carrito: {e}")
    db.rollback()
finally:
    db.close()
```

---

### Documentación del archivo `pedidos.py`

---

### Introducción

El archivo `pedidos.py` es un módulo encargado de la generación de datos de prueba relacionados con los pedidos en la base de datos. Proporciona funciones para crear pedidos basados en carritos existentes, generar códigos únicos para los pedidos y obtener pedidos en estado "Entregado". Este módulo asegura la coherencia temporal y respeta las reglas de negocio al procesar los datos.

---

### Funciones principales

#### `generate_pedido_codigo(timestamp_dt: datetime, counter: int) -> str`
**Descripción:**  
Genera un código único para un pedido utilizando la fecha y hora, un contador y un identificador aleatorio.

**Parámetros:**
- `timestamp_dt`: Marca de tiempo del pedido.
- `counter`: Contador para diferenciar pedidos creados en el mismo segundo.

**Retorno:**  
Código único del pedido en formato `PED-YYYYMMDDHHMMSS-counter-UUID`.

---

#### `create_pedidos(db: Session, todos_los_descuentos: List[Descuento], carritos: List[Carrito], porcentaje_conversion: float) -> List[Pedido]`
**Descripción:**  
Crea pedidos basados en registros de carritos existentes. Solo un porcentaje de los carritos se convierten en pedidos, mientras que el resto se consideran abandonados. Los pedidos se procesan en orden cronológico.

**Parámetros:**
- `db`: Sesión de base de datos.
- `todos_los_descuentos`: Lista de descuentos disponibles para aplicar a los pedidos.
- `carritos`: Lista de carritos existentes.
- `porcentaje_conversion`: Porcentaje de carritos que se convertirán en pedidos.

**Retorno:**  
Lista de objetos `Pedido` creados.

**Detalles:**
- Ordena los carritos por `fecha_actualizacion` para mantener coherencia temporal.
- Determina cuántos carritos se convertirán en pedidos según el porcentaje de conversión.
- Genera detalles del pedido, aplica descuentos y crea envíos asociados.

---

#### `get_pedidos_entregados(db: Session) -> list[Pedido]`
**Descripción:**  
Obtiene todos los pedidos que están en estado "Entregado".

**Parámetros:**
- `db`: Sesión de base de datos.

**Retorno:**  
Lista de objetos `Pedido` en estado "Entregado".

**Detalles:**
- Filtra los pedidos por estado `Entregado`.
- Devuelve una lista vacía si no hay pedidos en este estado.

---

### Configuración y dependencias

- **Librerías utilizadas:**
    - `logging`: Para registrar información sobre el proceso de generación.
    - `random`: Para generar valores aleatorios (ej. porcentaje de conversión).
    - `uuid`: Para generar identificadores únicos.
    - `datetime`, `timedelta`: Para manejar fechas y tiempos.
    - `decimal`: Para manejar valores monetarios.
    - `sqlalchemy.orm.Session`: Para interactuar con la base de datos.
    - `sqlalchemy.exc.SQLAlchemyError`, `sqlalchemy.exc.IntegrityError`: Para manejar errores de base de datos.
    - `Faker`: Para generar datos ficticios.

- **Dependencias internas:**
    - Modelos como `Pedido`, `Usuario`, `Carrito`, `Descuento`, `HistorialDescuento`.
    - Enums como `EstadoPedidoEnum`, `MetodoPagoEnum`.
    - Funciones auxiliares como `create_localizacion_for_user`, `create_detalles_for_pedido`, `create_envio_for_pedido`.

---

### Advertencias

- **Coherencia temporal:**  
  Los pedidos se procesan en orden cronológico para respetar las reglas de negocio y mantener consistencia en los datos.

- **Manejo de errores:**  
  Implementa bloques `try-except` para capturar y manejar excepciones durante las operaciones de base de datos.

- **Porcentaje de conversión:**  
  Ajusta el porcentaje de conversión para simular diferentes escenarios de abandono de carritos.

---

### Ejemplo de uso

```python
from sqlalchemy.orm import Session
from app.db.data_generation.pedidos import create_pedidos, get_pedidos_entregados
from app.models.carrito import Carrito
from app.models.descuento import Descuento

# Crear pedidos
carritos = [...]  # Lista de carritos obtenida previamente
descuentos = [...]  # Lista de descuentos disponibles
pedidos = create_pedidos(db=session, todos_los_descuentos=descuentos, carritos=carritos, porcentaje_conversion=0.75)

# Obtener pedidos entregados
pedidos_entregados = get_pedidos_entregados(db=session)
```
---

### Documentación del archivo `localizacion_pedido.py`

---

### Introducción

El archivo `localizacion_pedido.py` es un módulo dedicado a la generación de datos de prueba para la entidad `LocalizacionPedido` en la base de datos. Su función principal es crear registros de localizaciones (direcciones de envío) asociadas a usuarios, asegurando que estas localizaciones sean geográficamente coherentes dentro de Colombia y temporalmente válidas dentro del marco de la simulación.

---

### Funciones principales

#### `create_localizacion_for_user(db: Session, usuario: Usuario, max_fecha_localizacion: datetime, fecha_minima: Optional[datetime] = None) -> Optional[LocalizacionPedido]`
**Descripción:**  
Crea y guarda una nueva localización de pedido para un usuario específico. La localización se genera con datos geográficos aleatorios de Colombia y una fecha de registro dentro de un rango temporal especificado.

**Parámetros:**
- `db`: Sesión de base de datos SQLAlchemy.
- `usuario`: El objeto `Usuario` al que se asociará la localización.
- `max_fecha_localizacion`: La fecha máxima permitida para el registro de esta localización.
- `fecha_minima` (Opcional): La fecha mínima permitida para el registro de esta localización. Si no se proporciona, se usará la `fecha_registro` del usuario como límite inferior.

**Retorno:**  
Un objeto `LocalizacionPedido` si la creación fue exitosa, o `None` si ocurrió un error o no se pudo generar una fecha válida.

**Detalles:**
- Selecciona aleatoriamente un departamento y una de sus ciudades (junto con su código postal) del diccionario `departamentos_y_ciudades`.
- Genera una dirección de calle aleatoria utilizando la librería `Faker` (ej. "Carrera 10 #20-30").
- La `fecha_registro` de la localización se genera aleatoriamente. Debe ser posterior a `fecha_minima` (o `usuario.fecha_registro`) y anterior o igual a `max_fecha_localizacion`.
- Se asegura que la `fecha_registro` generada esté dentro de los límites globales de la simulación (`SIMULATION_START_DATE` y `SIMULATION_END_DATE`).
- La `fecha_actualizacion` de la localización se establece inicialmente igual a su `fecha_registro`.
- Si no se puede encontrar una ventana temporal válida para la `fecha_registro` o si ocurre un error durante la inserción en la base de datos, la función retorna `None` y realiza un `rollback`.

---

### Constantes y Variables Globales Clave

- `logger`: Instancia del `logging.Logger` para registrar información y errores.
- `fake`: Instancia de `Faker` configurada para "es\_CO", utilizada para generar direcciones aleatorias.
- `departamentos_y_ciudades`: Un diccionario que contiene una lista de departamentos de Colombia, y para cada departamento, una lista de ciudades con sus respectivos códigos postales. Esta estructura es la fuente para los datos geográficos de las localizaciones.
- `SIMULATION_START_DATE` (implícita): Fecha de inicio global para la generación de datos de simulación. Usada para validar la `fecha_registro`.
- `SIMULATION_END_DATE` (implícita): Fecha de fin global para la generación de datos de simulación. Usada para validar la `fecha_registro`.

---

### Configuración y dependencias

- **Librerías utilizadas:**
    - `logging`: Para el registro de información y errores.
    - `random`: Para la selección aleatoria de departamentos y ciudades.
    - `datetime`: Para la manipulación de fechas y tiempos.
    - `typing.Dict`, `typing.List`, `typing.Optional`: Para anotaciones de tipo.
    - `Faker`: Para la generación de datos ficticios (direcciones).
    - `sqlalchemy.orm.Session`: Para la interacción con la base de datos.
    - `sqlalchemy.exc.SQLAlchemyError`: Para el manejo de excepciones de SQLAlchemy.

- **Dependencias internas:**
    - `app.models.usuario.Usuario`: El modelo SQLAlchemy para la tabla de usuarios.
    - `app.models.localizacion_pedido.LocalizacionPedido`: El modelo SQLAlchemy para la tabla de localizaciones de pedido.
    - `app.db.data_generation.utils_datetime.get_random_datetime_in_range` (implícita): Función de utilidad para obtener una fecha y hora aleatoria dentro de un rango específico.
    - Constantes globales `SIMULATION_START_DATE` y `SIMULATION_END_DATE` (definidas probablemente en un módulo de configuración o `utils`).

---

### Advertencias

- **Coherencia Temporal:** Es crucial que `fecha_minima` y `max_fecha_localizacion` se establezcan correctamente para asegurar que la `fecha_registro` de la localización sea lógicamente consistente con otros eventos (ej. registro del usuario, creación del carrito/pedido). La función intenta validar esto contra `SIMULATION_START_DATE` y `SIMULATION_END_DATE`.
- **Datos Geográficos:** La calidad y variedad de los datos geográficos dependen enteramente del contenido del diccionario `departamentos_y_ciudades`.
- **Manejo de Errores:** La función incluye un bloque `try-except` para `SQLAlchemyError` y otras excepciones generales, realizando un `rollback` en caso de error para mantener la consistencia de la base de datos.

---

### Ejemplo de uso

```python
from sqlalchemy.orm import Session
from app.db.database import SessionLocal # o tu forma de obtener la sesión
from app.models.usuario import Usuario # Asumiendo que tienes un objeto Usuario
from app.db.data_generation.localizacion_pedido import create_localizacion_for_user
from datetime import datetime, timedelta

# Obtener una sesión de base de datos
db: Session = SessionLocal()

# Asumimos que 'un_usuario' es un objeto Usuario obtenido previamente
# y 'SIMULATION_END_DATE' está definida
un_usuario = db.query(Usuario).first() 
# SIMULATION_END_DATE = datetime(2025, 5, 1) # Ejemplo

if un_usuario:
    try:
        # Definir la ventana temporal para la localización
        # Por ejemplo, la localización debe crearse después del registro del usuario
        # y como máximo 10 días después, pero no más allá del fin de la simulación.
        fecha_min_loc = un_usuario.fecha_registro + timedelta(hours=1)
        fecha_max_loc = min(un_usuario.fecha_registro + timedelta(days=10), SIMULATION_END_DATE - timedelta(minutes=10))

        nueva_localizacion = create_localizacion_for_user(
            db=db,
            usuario=un_usuario,
            max_fecha_localizacion=fecha_max_loc,
            fecha_minima=fecha_min_loc
        )

        if nueva_localizacion:
            logger.info(f"Localización {nueva_localizacion.id} creada para usuario {un_usuario.id}")
            db.commit() # Commit si la operación es atómica aquí o manejada por un script superior
        else:
            logger.warning(f"No se pudo crear localización para usuario {un_usuario.id}")
            # No es necesario rollback aquí si create_localizacion_for_user ya lo hizo

    except Exception as e:
        logger.error(f"Error al crear localización: {e}")
        db.rollback() # Rollback general si es necesario
    finally:
        db.close()
else:
    logger.error("No se encontró un usuario para crear la localización.")

```
---

### Documentación del archivo `envios.py`

---

### Introducción

El archivo `envios.py` es un módulo responsable de la generación y gestión de datos de prueba para las entidades `Envio` e `HistorialEnvio` en la base de datos. Su función principal es simular la creación de envíos asociados a pedidos, incluyendo la asignación de una empresa de transporte, la generación de un código de seguimiento, el cálculo de costos de envío, la estimación de fechas de entrega y el registro del estado inicial del envío.

---

### Funciones principales

#### `create_envio_for_pedido(db: Session, pedido: Pedido, fecha_pedido: datetime, usuario_id: int) -> Tuple[Optional[Envio], Optional[HistorialEnvio]]`
**Descripción:**  
Crea un nuevo envío y su primer registro de historial para un pedido específico. Selecciona una empresa de transporte, genera un código de seguimiento, calcula el costo del envío y estima la fecha de entrega.

**Parámetros:**
- `db`: Sesión de base de datos SQLAlchemy.
- `pedido`: El objeto `Pedido` al que se asociará el envío.
- `fecha_pedido`: La fecha en que se realizó el pedido, usada como base para las fechas del envío.
- `usuario_id`: El ID del usuario asociado al pedido. (Nota: El objeto `pedido` ya contiene `usuario_id` y `id_localizacion`, que es crucial para el envío).

**Retorno:**  
Una tupla `(Envio, HistorialEnvio)` con los objetos creados si la operación fue exitosa, o `(None, None)` si ocurrió un error.

**Detalles:**
- Selecciona aleatoriamente una empresa de la lista `EMPRESAS_ENVIO`.
- Genera un código de seguimiento único para el envío.
- El costo del envío (`costo_envio`) se calcula (la lógica específica puede variar, por ejemplo, basándose en la localización del pedido obtenida a través de `pedido.id_localizacion`).
- La `fecha_registro` del envío se establece típicamente poco después de la `fecha_pedido`.
- La `fecha_estimada_entrega` se calcula sumando un número aleatorio de días (ej. 2-7 días) a la `fecha_pedido` o `fecha_registro` del envío.
- El estado inicial del envío se establece (ej. `EstadoEnvioEnum.EnPreparacion` o `EstadoEnvioEnum.PendienteDeEnvio`).
- Se crea un objeto `Envio` con estos datos y se asocia al `pedido.id`.
- Se crea un objeto `HistorialEnvio` que registra el estado inicial del envío, con su `fecha_evento` correspondiente a la `fecha_registro` del envío o ligeramente posterior.
- Ambas entidades (`Envio` e `HistorialEnvio`) se añaden a la sesión de la base de datos.
- La función debe manejar errores y realizar un `rollback` en caso de fallo para no dejar la base de datos en estado inconsistente.

---

### Constantes y Variables Globales Clave

- `logger`: Instancia del `logging.Logger` para registrar información y errores.
- `fake`: Instancia de `Faker` configurada para "es\_CO", utilizada para generar datos ficticios si es necesario (ej. notas adicionales para el envío).
- `EMPRESAS_ENVIO`: Una lista de cadenas con nombres de empresas de transporte predefinidas (ej. `["Servientrega", "Interrapidísimo", ...]`).
- `SIMULATION_START_DATE` (implícita): Fecha de inicio global para la generación de datos de simulación.
- `SIMULATION_END_DATE` (implícita): Fecha de fin global para la generación de datos de simulación.
- (Potenciales constantes adicionales para definir rangos de costos de envío, tiempos mínimos/máximos de entrega, etc.)

---

### Configuración y dependencias

- **Librerías utilizadas:**
    - `logging`: Para el registro de eventos.
    - `random`: Para la selección aleatoria (ej. empresa de envío, cálculo de días de entrega).
    - `datetime`, `timedelta`: Para la manipulación de fechas y tiempos.
    - `typing.Tuple`, `typing.Optional`, `typing.List`: Para anotaciones de tipo.
    - `Faker`: Para la generación de datos ficticios.
    - `sqlalchemy.orm.Session`: Para la interacción con la base de datos.
    - `sqlalchemy.exc.SQLAlchemyError`: Para el manejo de excepciones de SQLAlchemy.

- **Dependencias internas:**
    - `app.models.pedido.Pedido`: El modelo SQLAlchemy para la tabla de pedidos.
    - `app.models.envio.Envio`: El modelo SQLAlchemy para la tabla de envíos.
    - `app.models.envio.HistorialEnvio`: El modelo SQLAlchemy para la tabla de historial de envíos.
    - `app.models.localizacion_pedido.LocalizacionPedido` (implícita): Para obtener detalles de la dirección de envío a través del `pedido`.
    - `app.models.enums.EstadoEnvioEnum`: Enum para los posibles estados de un envío.
    - `app.db.data_generation.utils_datetime.get_random_datetime_in_range` (potencialmente): Para generar fechas dentro de rangos.

---

### Advertencias

- **Coherencia Temporal:** Es crucial que las fechas asociadas al envío (`fecha_registro`, `fecha_estimada_entrega`) y al historial de envío (`fecha_evento`) sean lógicamente consistentes con la `fecha_pedido` y se encuentren dentro de los límites de la simulación.
- **Cálculo de Costos y Tiempos:** La lógica para calcular el `costo_envio` y la `fecha_estimada_entrega` debe ser realista para la simulación. Estos pueden depender de factores como la distancia (derivada de la localización), peso/dimensiones del paquete (inferido de los productos del pedido), etc.
- **Manejo de Errores:** La función `create_envio_for_pedido` debe incluir un manejo robusto de excepciones (ej. `SQLAlchemyError`) y realizar `db.rollback()` en caso de error para mantener la integridad de los datos.
- **Actualización de Estados:** Este módulo se centra en la creación inicial. Un sistema completo de simulación de envíos también requeriría funciones para actualizar el estado del envío a lo largo del tiempo (ej. de "En preparación" a "Enviado", "En tránsito", "Entregado"), lo cual podría estar en este módulo o en uno dedicado a la progresión de estados.

---

### Ejemplo de uso

```python
from sqlalchemy.orm import Session
from app.db.database import SessionLocal # o tu forma de obtener la sesión
from app.models.pedido import Pedido # Asumiendo que tienes un objeto Pedido
from app.db.data_generation.envios import create_envio_for_pedido
from datetime import datetime
import logging # Asegúrate de tener el logger configurado

logger = logging.getLogger(__name__)

# Obtener una sesión de base de datos
db: Session = SessionLocal()

# Asumimos que 'un_pedido' es un objeto Pedido obtenido previamente
# y 'fecha_creacion_pedido' es la fecha en que se creó el pedido.
# un_pedido = db.query(Pedido).first() # Ejemplo
# fecha_creacion_pedido = un_pedido.fecha_registro # Ejemplo

# Este es un ejemplo simplificado. En el flujo real, 'un_pedido' y 'fecha_creacion_pedido'
# vendrían del proceso de creación de pedidos.

# Ejemplo de obtención de un pedido (debe existir en la BD para este ejemplo)
un_pedido = db.query(Pedido).order_by(Pedido.id.desc()).first()

if un_pedido:
    fecha_creacion_pedido = un_pedido.fecha_registro # Usar la fecha del pedido

    try:
        nuevo_envio, nuevo_historial_envio = create_envio_for_pedido(
            db=db,
            pedido=un_pedido,
            fecha_pedido=fecha_creacion_pedido,
            usuario_id=un_pedido.usuario_id # El pedido ya tiene el usuario_id
        )

        if nuevo_envio and nuevo_historial_envio:
            logger.info(f"Envío {nuevo_envio.id} (código: {nuevo_envio.codigo_seguimiento}) "
                        f"e historial inicial {nuevo_historial_envio.id} creados para el pedido {un_pedido.id}.")
            db.commit() # Commit si la operación es atómica aquí o manejada por un script superior
        else:
            logger.warning(f"No se pudo crear el envío para el pedido {un_pedido.id}.")
            # El rollback debería ser manejado dentro de create_envio_for_pedido o aquí si es necesario.

    except Exception as e:
        logger.error(f"Error al crear el envío para el pedido {un_pedido.id}: {e}", exc_info=True)
        db.rollback() # Rollback general si es necesario
    finally:
        db.close()
else:
    logger.error("No se encontró un pedido para crear el envío.")

```
---

### Documentación del archivo `detalle_pedido.py`

---

### Introducción

El archivo `detalle_pedido.py` es un módulo fundamental en el proceso de generación de datos de simulación, encargado de crear los detalles individuales de los productos que componen un pedido. Este módulo trabaja en conjunto con la creación de pedidos, seleccionando productos, determinando cantidades, calculando precios y subtotales, y asegurando la coherencia con el inventario disponible.

---

### Funciones principales

#### `calcular_fecha_entregado(fecha_creacion_pedido: datetime, fecha_referencia_anterior: datetime) -> datetime`
**Descripción:**  
Calcula una fecha estimada para que un pedido sea marcado como "Entregado". Esta fecha se genera aleatoriamente dentro de un rango de días a partir de la fecha de creación del pedido, asegurando que sea posterior a una fecha de referencia anterior (por ejemplo, la fecha de envío) y no exceda la fecha de fin de la simulación.

**Parámetros:**
- `fecha_creacion_pedido`: La fecha y hora en que se creó el pedido.
- `fecha_referencia_anterior`: La fecha y hora del estado previo del pedido (ej. fecha de envío), utilizada como límite inferior para la nueva fecha.

**Retorno:**  
Un objeto `datetime` que representa la fecha calculada para el estado "Entregado".

**Detalles:**
- Añade un delta aleatorio de 4 a 14 días a la `fecha_creacion_pedido`.
- Añade también una cantidad aleatoria de segundos para mayor variabilidad.
- Asegura que la fecha calculada sea estrictamente posterior a `fecha_referencia_anterior`.
- Limita la fecha resultante para que no supere `SIMULATION_END_DATE`.

---

#### `create_detalles_for_pedido(db: Session, pedido: Pedido, productos_disponibles: List[Producto], fecha_creacion_pedido: datetime, max_productos_por_pedido: int = 5, probabilidad_varios_productos: float = 0.6) -> Tuple[List[DetallePedido], Decimal, Decimal]`
**Descripción:**  
Crea y guarda los registros de `DetallePedido` para un pedido dado. Selecciona aleatoriamente productos de la lista de disponibles, determina la cantidad de cada uno, calcula el precio con posibles descuentos (si aplica la lógica, aunque no explícito en la firma), y actualiza el inventario. Devuelve la lista de detalles creados, el subtotal del pedido y el total (que podría ser igual al subtotal si no hay otros cargos/descuentos a nivel de pedido manejados aquí).

**Parámetros:**
- `db`: Sesión de base de datos SQLAlchemy.
- `pedido`: El objeto `Pedido` para el cual se están creando los detalles.
- `productos_disponibles`: Una lista de objetos `Producto` que están activos y pueden ser añadidos al pedido.
- `fecha_creacion_pedido`: La fecha y hora en que se creó el pedido, usada para la `fecha_registro` de los detalles y para operaciones de inventario.
- `max_productos_por_pedido` (Opcional): Número máximo de tipos de productos diferentes que puede tener un pedido. Por defecto es 5.
- `probabilidad_varios_productos` (Opcional): Probabilidad de que un pedido contenga más de un tipo de producto. Por defecto es 0.6.

**Retorno:**  
Una tupla `(List[DetallePedido], Decimal, Decimal)` que contiene:
- La lista de objetos `DetallePedido` creados y guardados.
- El `subtotal_pedido` calculado (suma de `precio_unitario * cantidad` para todos los detalles).
- El `total_pedido` (que en esta función parece ser igual al `subtotal_pedido`).

**Detalles:**
- Decide aleatoriamente el número de productos distintos para el pedido (entre 1 y `max_productos_por_pedido`).
- Para cada producto a añadir:
    - Selecciona un producto aleatorio de `productos_disponibles` que no haya sido añadido ya al mismo pedido.
    - Determina una cantidad aleatoria (generalmente entre 1 y 3).
    - Verifica la disponibilidad de stock usando `validar_disponibilidad_producto`. Si no hay suficiente, intenta con otro producto o reduce la cantidad.
    - El `precio_unitario` en el detalle se toma del `precio_venta` del producto.
    - Calcula el `subtotal_detalle` (`precio_unitario * cantidad`).
    - Crea el objeto `DetallePedido` con la `fecha_registro` igual a `fecha_creacion_pedido`.
    - Llama a `actualizar_inventario_por_pedido` para decrementar el stock del producto vendido.
    - Acumula los subtotales para calcular el `subtotal_pedido` y `total_pedido`.
- Si no se pueden añadir productos (ej. por falta de stock persistente), puede retornar listas vacías y totales cero.
- Maneja errores durante el proceso, incluyendo `SQLAlchemyError`, y realiza `rollback` si es necesario.

---

### Constantes y Variables Globales Clave

- `logger`: Instancia del `logging.Logger` para registrar información y errores.
- `SIMULATION_END_DATE` (implícita, usada en `calcular_fecha_entregado`): Fecha de fin global para la generación de datos de simulación.
- `MAX_INTENTOS_PRODUCTO`: Constante interna que define cuántas veces intentar seleccionar un producto válido para un detalle antes de desistir.

---

### Configuración y dependencias

- **Librerías utilizadas:**
    - `logging`: Para el registro de eventos.
    - `random`: Para la selección aleatoria de productos, cantidades y cálculos de fechas.
    - `datetime`, `timedelta`: Para la manipulación de fechas y tiempos.
    - `typing.List`, `typing.Tuple`, `Decimal`: Para anotaciones de tipo y manejo de valores monetarios.
    - `sqlalchemy.orm.Session`: Para la interacción con la base de datos.
    - `sqlalchemy.exc.SQLAlchemyError`: Para el manejo de excepciones de SQLAlchemy.

- **Dependencias internas:**
    - `app.models.pedido.Pedido`: El modelo SQLAlchemy para la tabla de pedidos.
    - `app.models.producto.Producto`: El modelo SQLAlchemy para la tabla de productos.
    - `app.models.detalle_pedido.DetallePedido`: El modelo SQLAlchemy para la tabla de detalles de pedido.
    - `app.db.data_generation.inventario.validar_disponibilidad_producto`: Para comprobar si hay stock suficiente de un producto.
    - `app.db.data_generation.inventario.actualizar_inventario_por_pedido`: Para actualizar el stock después de añadir un producto al pedido.
    - `SIMULATION_END_DATE` (constante global, probablemente de `app.db.data_generation.utils_datetime` o un archivo de configuración).

---

### Advertencias

- **Coherencia de Stock:** Es crucial que la verificación de disponibilidad (`validar_disponibilidad_producto`) y la actualización de inventario (`actualizar_inventario_por_pedido`) se realicen correctamente para evitar inconsistencias como vender productos sin stock.
- **Coherencia Temporal:** La `fecha_registro` de los `DetallePedido` debe ser consistente con la `fecha_creacion_pedido`. Las fechas calculadas por `calcular_fecha_entregado` también deben ser lógicamente secuenciales.
- **Manejo de Errores:** La función `create_detalles_for_pedido` debe manejar robustamente los casos en los que no se pueden añadir productos (ej. falta de stock) y los errores de base de datos, realizando `rollback` para mantener la integridad.
- **Transacciones:** Las operaciones de base de datos (creación de detalles, actualización de inventario) se añaden a la sesión. El `commit` final generalmente es manejado por la función que orquesta la creación del pedido completo (ej. en `pedidos.py`).

---

### Ejemplo de uso

```python
from sqlalchemy.orm import Session
from app.db.database import SessionLocal # o tu forma de obtener la sesión
from app.models.pedido import Pedido
from app.models.producto import Producto
from app.db.data_generation.detalle_pedido import create_detalles_for_pedido, calcular_fecha_entregado
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Obtener una sesión de base de datos
db: Session = SessionLocal()

# Asumimos que 'un_pedido' es un objeto Pedido ya creado y persistido (con ID)
# y 'productos_activos' es una lista de objetos Producto disponibles.
# 'fecha_pedido_actual' es la fecha de creación del pedido.

# Ejemplo de obtención (estos objetos deben existir y ser válidos)
un_pedido = db.query(Pedido).order_by(Pedido.id.desc()).first()
productos_activos = db.query(Producto).filter(Producto.estado_producto == "Activo").limit(20).all()

if un_pedido and productos_activos:
    fecha_pedido_actual = un_pedido.fecha_registro

    try:
        detalles_creados, subtotal, total_pedido = create_detalles_for_pedido(
            db=db,
            pedido=un_pedido,
            productos_disponibles=productos_activos,
            fecha_creacion_pedido=fecha_pedido_actual
        )

        if detalles_creados:
            logger.info(f"Se crearon {len(detalles_creados)} detalles para el pedido {un_pedido.id}.")
            logger.info(f"Subtotal: {subtotal}, Total: {total_pedido}")
            
            # Actualizar el pedido con los totales (si es necesario aquí)
            # un_pedido.subtotal = subtotal
            # un_pedido.total = total_pedido
            # db.add(un_pedido)
            
            # Ejemplo de cálculo de fecha de entrega (asumiendo una fecha de envío)
            fecha_envio_simulada = fecha_pedido_actual + timedelta(days=1) # Ejemplo
            fecha_estimada_entrega = calcular_fecha_entregado(fecha_pedido_actual, fecha_envio_simulada)
            logger.info(f"Fecha estimada de entrega para el pedido {un_pedido.id}: {fecha_estimada_entrega}")

            db.commit() # Commit si esta operación es atómica o manejada por un script superior
        else:
            logger.warning(f"No se pudieron crear detalles para el pedido {un_pedido.id}.")
            db.rollback() # Rollback si no se crearon detalles

    except Exception as e:
        logger.error(f"Error al crear detalles para el pedido {un_pedido.id}: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()
else:
    logger.error("No se encontró un pedido o productos activos para crear detalles.")

```
---

### Documentación del archivo `comentarios.py`

---

### Introducción

El archivo `comentarios.py` es un módulo encargado de la generación de datos de prueba para la entidad `Comentario` en la base de datos. Su función principal es simular la creación de comentarios y calificaciones por parte de los usuarios sobre los productos que han adquirido y recibido a través de pedidos. Este módulo asegura la coherencia temporal, asociando los comentarios a pedidos entregados y usuarios correspondientes.

---

### Funciones principales

#### `create_comentarios(db: Session, pedidos_entregados: List[Pedido], usuarios_clientes: List[Usuario], prob_comentar: float = 0.7) -> List[Comentario]`
**Descripción:**  
Genera y guarda comentarios para los productos incluidos en los pedidos que han sido marcados como "Entregado". No todos los productos de todos los pedidos entregados recibirán un comentario, esto se determina por la probabilidad `prob_comentar`.

**Parámetros:**
- `db`: Sesión de base de datos SQLAlchemy.
- `pedidos_entregados`: Una lista de objetos `Pedido` que ya han sido procesados y tienen un estado de "Entregado" y una `fecha_entrega` establecida.
- `usuarios_clientes`: Una lista de objetos `Usuario` (clientes) que podrían haber realizado los pedidos. Se utilizará para asociar el comentario al usuario correcto.
- `prob_comentar` (Opcional): Probabilidad (entre 0 y 1) de que un producto en un pedido entregado reciba un comentario. Por defecto es 0.7 (70%).

**Retorno:**  
Una lista de los objetos `Comentario` que fueron creados y guardados en la base de datos.

**Detalles:**
- Itera sobre cada pedido en `pedidos_entregados`.
- Para cada `DetallePedido` dentro de un pedido entregado:
    - Se decide aleatoriamente (basado en `prob_comentar`) si se generará un comentario para ese producto.
    - Se busca al usuario que realizó el pedido.
    - Se genera una calificación aleatoria para el producto (ej. entre 1 y 5 estrellas).
    - Se genera un título y un texto para el comentario utilizando la librería `Faker`. La longitud y el contenido del texto pueden variar.
    - La `fecha_creacion` del comentario se genera aleatoriamente, asegurando que sea posterior a la `fecha_entrega` del pedido y anterior a `SIMULATION_END_DATE`.
    - Se crea un objeto `Comentario` con el `id_usuario`, `id_producto`, `id_pedido`, calificación, título, texto y `fecha_creacion`.
    - El comentario se añade a la sesión de la base de datos.
- Maneja posibles errores durante la creación y persistencia de los comentarios.

---

### Constantes y Variables Globales Clave

- `logger`: Instancia del `logging.Logger` para registrar información y errores.
- `fake`: Instancia de `Faker` configurada para "es\_ES" o "es\_CO", utilizada para generar texto de comentarios.
- `MIN_RATING_COMMENT`: Calificación mínima para un comentario (ej. 1).
- `MAX_RATING_COMMENT`: Calificación máxima para un comentario (ej. 5).
- `MIN_DAYS_AFTER_DELIVERY_FOR_COMMENT`: Número mínimo de días después de la entrega para que se pueda registrar un comentario.
- `MAX_DAYS_AFTER_DELIVERY_FOR_COMMENT`: Número máximo de días después de la entrega para que se pueda registrar un comentario.
- `SIMULATION_END_DATE` (implícita): Fecha de fin global para la generación de datos de simulación, usada como límite superior para la fecha del comentario.

---

### Configuración y dependencias

- **Librerías utilizadas:**
    - `logging`: Para el registro de información y errores.
    - `random`: Para la generación de números aleatorios (calificaciones, decisión de comentar, selección de fechas).
    - `datetime`, `timedelta`: Para la manipulación de fechas y tiempos.
    - `typing.List`, `typing.Optional`: Para anotaciones de tipo.
    - `Faker`: Para la generación de texto ficticio para los comentarios.
    - `sqlalchemy.orm.Session`: Para la interacción con la base de datos.
    - `sqlalchemy.exc.SQLAlchemyError`: Para el manejo de excepciones de SQLAlchemy.

- **Dependencias internas:**
    - `app.models.comentario.Comentario`: El modelo SQLAlchemy para la tabla de comentarios.
    - `app.models.pedido.Pedido`: El modelo SQLAlchemy para la tabla de pedidos.
    - `app.models.detalle_pedido.DetallePedido`: El modelo SQLAlchemy para la tabla de detalles de pedido.
    - `app.models.usuario.Usuario`: El modelo SQLAlchemy para la tabla de usuarios.
    - `app.models.producto.Producto`: El modelo SQLAlchemy para la tabla de productos.
    - `app.db.data_generation.utils_datetime.get_random_datetime_in_range`: Función de utilidad para obtener una fecha y hora aleatoria dentro de un rango específico.
    - `SIMULATION_END_DATE` (constante global, probablemente de `app.db.data_generation.utils_datetime` o un archivo de configuración).

---

### Advertencias

- **Coherencia Temporal:** Es crucial que la `fecha_creacion` del comentario sea lógicamente posterior a la `fecha_entrega` del pedido asociado y dentro de los límites de la simulación.
- **Asociación Correcta:** El comentario debe estar correctamente asociado al `id_usuario` que realizó el pedido, al `id_producto` comentado y al `id_pedido` correspondiente.
- **Disponibilidad de Datos Previos:** Esta función depende de que existan pedidos entregados y usuarios. Si las listas `pedidos_entregados` o `usuarios_clientes` están vacías, no se generarán comentarios.
- **Manejo de Errores:** La función debe incluir bloques `try-except` para `SQLAlchemyError` y realizar `rollback` en caso de error para mantener la consistencia de la base de datos.

---

### Ejemplo de uso

```python
from sqlalchemy.orm import Session
from app.db.database import SessionLocal # o tu forma de obtener la sesión
from app.db.data_generation.comentarios import create_comentarios
from app.db.data_generation.pedidos import get_pedidos_entregados # Para obtener pedidos
from app.db.data_generation.usuarios import get_usuarios_activos_clientes # Para obtener usuarios
from app.models.pedido import Pedido # Tipado
from app.models.usuario import Usuario # Tipado
import logging

logger = logging.getLogger(__name__)

# Obtener una sesión de base de datos
db: Session = SessionLocal()

try:
    # Obtener pedidos entregados (esto asume que ya se han generado y procesado pedidos)
    lista_pedidos_entregados: List[Pedido] = get_pedidos_entregados(db)
    
    # Obtener usuarios clientes (esto asume que ya se han generado usuarios)
    lista_usuarios_clientes: List[Usuario] = get_usuarios_activos_clientes(db)

    if lista_pedidos_entregados and lista_usuarios_clientes:
        # Crear comentarios
        comentarios_creados = create_comentarios(
            db=db,
            pedidos_entregados=lista_pedidos_entregados,
            usuarios_clientes=lista_usuarios_clientes,
            prob_comentar=0.65 # Opcional: probabilidad del 65%
        )
        logger.info(f"Se crearon {len(comentarios_creados)} comentarios.")
        
        # El commit generalmente se maneja en el script principal (seed_data.py)
        # db.commit()
    else:
        logger.info("No hay pedidos entregados o usuarios clientes para generar comentarios.")

except Exception as e:
    logger.error(f"Error al generar comentarios: {e}", exc_info=True)
    db.rollback()
finally:
    db.close()
```
---

### Documentación del archivo `ai_generator.py`

---

### Introducción

El archivo `ai_generator.py` es un módulo que interactúa con modelos de inteligencia artificial para generar contenido dinámico como nombres, descripciones, imágenes y comentarios. Utiliza la librería `pydantic_ai` para configurar agentes de IA y realizar solicitudes a APIs externas como OpenAI y Pollinations.

---

### Funciones principales

#### `generar_nombre_producto_ia(categoria: str, fragancia: str) -> str`
**Descripción:**  
Genera un nombre único y atractivo para un producto utilizando IA.

**Parámetros:**
- `categoria`: Categoría del producto.
- `fragancia`: Fragancia del producto.

**Retorno:**  
Un nombre generado para el producto.

---

#### `generar_descripcion_producto_ia(nombre: str, categoria: str, fragancia: str) -> str`
**Descripción:**  
Genera una descripción breve y evocadora para un producto utilizando IA.

**Parámetros:**
- `nombre`: Nombre del producto.
- `categoria`: Categoría del producto.
- `fragancia`: Fragancia del producto.

**Retorno:**  
Una descripción generada para el producto.

---

#### `generate_image_pollinations(categoria: str, tamanio: str, fragancia: str, descripcion_producto: str) -> str`
**Descripción:**  
Genera una imagen profesional de un producto utilizando Pollinations.ai y devuelve una URL acortada.

**Parámetros:**
- `categoria`: Categoría del producto.
- `tamanio`: Tamaño del producto.
- `fragancia`: Fragancia principal del producto.
- `descripcion_producto`: Descripción del producto.

**Retorno:**  
Una URL acortada que redirecciona a la imagen generada.

---

#### `generate_descripcion_localizacion_ia() -> str`
**Descripción:**  
Genera una descripción complementaria para una dirección de entrega utilizando IA.

**Retorno:**  
Una descripción generada para la localización.

---

#### `generate_notas_entrega_ia() -> str`
**Descripción:**  
Genera notas de entrega breves y precisas para un pedido utilizando IA.

**Retorno:**  
Notas de entrega generadas.

---

#### `generate_comentario_ia(context: str) -> str`
**Descripción:**  
Genera un comentario breve y auténtico sobre un producto utilizando IA.

**Parámetros:**
- `context`: Contexto para la generación del comentario.

**Retorno:**  
Un comentario generado.

---

### Configuración y dependencias

- **Librerías utilizadas:**
  - `logging`: Para el registro de eventos y errores.
  - `httpx`: Para realizar solicitudes HTTP.
  - `pydantic_ai`: Para interactuar con modelos de IA.
  - `urllib.parse`: Para codificar parámetros de URL.

- **Dependencias internas:**
  - `app.core.config`: Configuración global del proyecto.
  - `app.core.tasks.APIResponseError`: Manejo de errores en solicitudes API.

---

### Advertencias

- **Manejo de Errores:** Las funciones que interactúan con APIs externas deben manejar excepciones como `httpx.RequestError` y `httpx.HTTPStatusError` para evitar interrupciones en el flujo.
- **Calidad del Contenido:** La calidad del contenido generado depende de los modelos de IA configurados y los prompts proporcionados.
- **Límites de API:** Asegúrate de respetar los límites de uso de las APIs externas como OpenAI y Pollinations.

---

### Ejemplo de uso

```python
from app.core.ai_generators import generar_nombre_producto_ia, generate_comentario_ia

# Generar un nombre para un producto
nombre_producto = generar_nombre_producto_ia(categoria="Velas aromáticas", fragancia="Lavanda")

# Generar un comentario para un producto
contexto = "Producto: Vela Lavanda, Descripción: Relajante y suave, Categoría: Velas aromáticas, Calificación: 5"
comentario = generate_comentario_ia(context=contexto)

print(nombre_producto)
print(comentario)
```
---

### Documentación del archivo `utils_datetime.py`

---

### Introducción

El archivo `utils_datetime.py` contiene funciones utilitarias para la manipulación de fechas y tiempos. Estas funciones son utilizadas en diferentes módulos del proyecto para generar fechas aleatorias dentro de rangos específicos, calcular intervalos de tiempo y validar coherencia temporal en la simulación de datos.

---

### Funciones principales

#### `get_random_datetime_in_range(start_date: datetime, end_date: datetime) -> datetime`
**Descripción:**  
Genera una fecha y hora aleatoria dentro de un rango especificado.

**Parámetros:**
- `start_date`: Fecha y hora inicial del rango.
- `end_date`: Fecha y hora final del rango.

**Retorno:**  
Un objeto `datetime` aleatorio dentro del rango especificado.

**Detalles:**
- Utiliza `random.randint` para calcular un delta aleatorio en segundos entre `start_date` y `end_date`.
- Asegura que la fecha generada esté dentro de los límites proporcionados.

---

#### `calculate_days_difference(date1: datetime, date2: datetime) -> int`
**Descripción:**  
Calcula la diferencia en días entre dos fechas.

**Parámetros:**
- `date1`: Primera fecha.
- `date2`: Segunda fecha.

**Retorno:**  
Un entero que representa la cantidad de días entre `date1` y `date2`.

**Detalles:**
- Devuelve el valor absoluto de la diferencia en días para evitar resultados negativos.

---

#### `is_date_in_range(date: datetime, start_date: datetime, end_date: datetime) -> bool`
**Descripción:**  
Verifica si una fecha específica está dentro de un rango de fechas.

**Parámetros:**
- `date`: Fecha a verificar.
- `start_date`: Fecha inicial del rango.
- `end_date`: Fecha final del rango.

**Retorno:**  
`True` si la fecha está dentro del rango, `False` en caso contrario.

**Detalles:**
- Compara la fecha proporcionada con los límites del rango.

---

### Configuración y dependencias

- **Librerías utilizadas:**
  - `random`: Para la generación de valores aleatorios.
  - `datetime`: Para la manipulación de fechas y tiempos.
  - `logging`: Para registrar información y errores.

---

### Advertencias

- **Coherencia Temporal:** Las funciones deben ser utilizadas con parámetros válidos para evitar errores en la simulación de datos.
- **Validación de Rangos:** Asegúrate de que `start_date` sea anterior a `end_date` al usar funciones que dependen de rangos de fechas.

---

### Ejemplo de uso

```python
from datetime import datetime, timedelta
from app.db.data_generation.utils_datetime import get_random_datetime_in_range, calculate_days_difference, is_date_in_range

# Generar una fecha aleatoria dentro de un rango
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)
random_date = get_random_datetime_in_range(start_date, end_date)
print(f"Fecha aleatoria: {random_date}")

# Calcular diferencia en días entre dos fechas
date1 = datetime(2023, 5, 1)
date2 = datetime(2023, 5, 10)
days_difference = calculate_days_difference(date1, date2)
print(f"Diferencia en días: {days_difference}")

# Verificar si una fecha está dentro de un rango
date_to_check = datetime(2023, 6, 15)
is_in_range = is_date_in_range(date_to_check, start_date, end_date)
print(f"¿Está en rango?: {is_in_range}")
```
---

### Documentación del archivo `utils.py`

---

### Introducción

El archivo `utils.py` contiene funciones utilitarias para la manipulación de cadenas de texto. Estas funciones son utilizadas en diferentes módulos del proyecto para sanitizar y transformar cadenas, asegurando que cumplan con requisitos específicos como formato para correos electrónicos.

---

### Funciones principales

#### `sanear_string_para_correo(texto: str) -> str`
**Descripción:**  
Sanea una cadena de texto para ser utilizada como parte de un correo electrónico.

**Parámetros:**
- `texto`: Cadena de texto a sanitizar.

**Retorno:**  
Una cadena de texto transformada que cumple con los siguientes criterios:
- Convertida a minúsculas.
- Sin tildes ni caracteres especiales.
- Espacios reemplazados por guiones bajos.
- Solo caracteres alfanuméricos y guiones bajos permitidos.

**Detalles:**
- Utiliza `unicodedata.normalize` para eliminar tildes y caracteres especiales.
- Reemplaza espacios y múltiples guiones bajos con un único guion bajo.
- Elimina caracteres no alfanuméricos excepto el guion bajo.

---

### Configuración y dependencias

- **Librerías utilizadas:**
  - `re`: Para expresiones regulares.
  - `unicodedata`: Para normalización de texto.

---

### Advertencias

- **Formato de Entrada:** La función asume que la entrada es una cadena válida. Si se pasa un tipo diferente, podría generar errores.
- **Uso en Correos Electrónicos:** Aunque la función transforma el texto para cumplir con requisitos básicos, no valida que el resultado sea un correo electrónico válido.

---

### Ejemplo de uso

```python
from app.db.data_generation.utils import sanear_string_para_correo

# Saneando una cadena para uso en correos electrónicos
texto_original = "José Pérez López"
texto_saneado = sanear_string_para_correo(texto_original)
print(texto_saneado)  # Resultado: jose_perez_lopez
```