### Documentación Técnica: `seed_data.py`

#### Introducción

El script `seed_data.py` es el orquestador principal para poblar la base de datos con datos de simulación. Su objetivo
es generar un conjunto de datos coherente y realista que represente la actividad de una tienda en línea, incluyendo
usuarios, productos, inventario, pedidos, descuentos, y más. Este script invoca secuencialmente diversos módulos
especializados en la generación de cada tipo de entidad.

---

#### Componentes Principales y Flujo de Generación

El script `seed_data.py` coordina la ejecución de varios módulos de generación de datos en un orden específico para
mantener la integridad referencial y la coherencia temporal. Los principales módulos involucrados y el flujo general
son:

1. **Configuración Inicial:**
    * Carga de variables de entorno y configuración de logging.
    * Inicialización de la sesión de base de datos.

2. **Generación de Datos Base:**
    * **Usuarios (`usuarios.py`):** Crea usuarios de diferentes roles (clientes, administradores), incluyendo datos
      personales ficticios y fechas de registro.
    * **Productos (`productos.py`):** Genera un catálogo de productos con nombres, descripciones (potencialmente usando
      IA), categorías, precios y fechas de creación.
    * **Inventario Inicial (`inventario.py`):** Establece el stock inicial para cada producto creado.

3. **Generación de Datos de Soporte y Marketing:**
    * **Descuentos (`descuentos.py`):** Crea campañas de descuento basadas en fechas especiales y rangos de tiempo, con
      códigos y porcentajes variables.

4. **Simulación de Actividad del Usuario:**
    * **Carritos de Compra (`carrito.py`):** Simula la acción de usuarios añadiendo productos a sus carritos,
      verificando disponibilidad de stock.
    * **Localizaciones de Pedido (`localizacion_pedido.py`):** Genera direcciones de envío para los usuarios.
    * **Pedidos (`pedidos.py`):** Convierte un porcentaje de los carritos en pedidos. Esto implica:
        * **Detalles de Pedido (`detalle_pedido.py`):** Crea los ítems específicos de cada pedido, actualiza el
          inventario y calcula subtotales.
        * Aplicación de descuentos si corresponde.
        * **Envíos (`envios.py`):** Crea registros de envío para los pedidos, asignando empresas de transporte, códigos
          de seguimiento y estimando fechas de entrega. Incluye la creación del historial inicial del envío.
    * **Actualización de Estados:** Simula la progresión de los pedidos y envíos a través de diferentes estados (ej.
      Pagado, Enviado, Entregado) a lo largo del tiempo.

5. **Generación de Datos Post-Venta:**
    * **Comentarios (`comentarios.py`):** Genera comentarios y calificaciones de productos por parte de usuarios para
      pedidos que han sido entregados.

6. **Finalización:**
    * Realiza `commit` de todas las transacciones a la base de datos.
    * Cierra la sesión de base de datos.
    * Reporta un resumen de los datos generados.

---

#### Configuración Clave

La simulación se rige por constantes globales definidas principalmente en los módulos individuales y, en algunos casos,
en un archivo de configuración central (ej. `config.py` o `utils_datetime.py` para fechas de simulación). Estas
incluyen:

* `SIMULATION_START_DATE` y `SIMULATION_END_DATE`: Definen el marco temporal general para todos los eventos generados.
* Umbrales y probabilidades: Controlan la cantidad de datos generados (ej. número de usuarios, porcentaje de conversión
  de carritos a pedidos, probabilidad de comentar).
* Parámetros de IA: Si se usa `ai_generator.py`, las claves API y configuraciones del modelo son cruciales.

---

#### Ejecución del Script

Para poblar la base de datos, el script `seed_data.py` se ejecuta directamente desde la raíz del proyecto. Asegúrate de
que todas las dependencias estén instaladas y la base de datos esté configurada correctamente. La ejecución se realiza
con el siguiente comando en la terminal:

```bash
python seed_data.py
```

Es importante asegurarse de que la base de datos esté accesible y el esquema haya sido creado previamente.

---

#### Consideraciones

* **Tiempo de Ejecución:** La generación de un gran volumen de datos puede tomar un tiempo considerable.
* **Consistencia de Datos:** El orden de ejecución de los módulos es vital para mantener la integridad referencial.
* **Estado en Memoria:** Algunos módulos (ej. `inventario.py` con `ultimas_reposiciones`) pueden mantener estado en
  memoria que se reinicia con cada ejecución del script.
* **Recursos:** La generación de imágenes mediante IA (`ai_generator.py`) puede consumir recursos y requerir
  conectividad a internet y APIs válidas.
* **Errores:** El script incluye manejo de errores y `rollback` de transacciones para evitar estados inconsistentes en
  la base de datos en caso de fallo. Los logs son fundamentales para diagnosticar problemas.

---