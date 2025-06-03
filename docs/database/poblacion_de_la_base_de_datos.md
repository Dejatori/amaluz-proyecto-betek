# Población de la Base de Datos: Coherencia Temporal

Este documento detalla el orden y las consideraciones temporales para poblar la base de datos, asegurando que las fechas
de registro, actualización y otros eventos sean lógicamente consistentes entre las entidades.

**Principio Fundamental de Coherencia Temporal:**

La `fecha_registro` de una entidad dependiente nunca puede ser anterior a la `fecha_registro` (o una fecha de evento
relevante como `fecha_actualizacion` o `fecha_cambio`) de las entidades de las que depende. De manera similar, cualquier
`fecha_actualizacion` debe ser posterior o igual a la `fecha_registro` de la misma entidad, y las actualizaciones
subsecuentes deben ser cronológicamente posteriores.

Las funciones auxiliares en `app/db/data_generation/utils_datetime.py` (`get_random_datetime`,
`generate_initial_update_datetime`, `generate_subsequent_update_datetime`) son esenciales para implementar estas reglas
correctamente. Se asume la existencia de `SIMULATION_START_DATE` y `SIMULATION_END_DATE` como cotas temporales globales.

**Orden de Población y Reglas Temporales por Entidad:**

1. **Entidades Fundamentales (Base de la Cronología)**

* **`proveedores`**:
  *   `proveedores.fecha_registro`: Generada entre `SIMULATION_START_DATE` y `SIMULATION_END_DATE`.
    * Ej: `get_random_datetime(SIMULATION_START_DATE, SIMULATION_END_DATE)`
      *   `proveedores.fecha_actualizacion`: Inicialmente generada poco después de `proveedores.fecha_registro`.
    * Ej: `generate_initial_update_datetime(registration_datetime=proveedores.fecha_registro)`
* **`usuarios`**:
  *   `usuarios.fecha_registro`: Generada entre `SIMULATION_START_DATE` y `SIMULATION_END_DATE`.
  *   `usuarios.fecha_actualizacion`: Inicialmente generada poco después de `usuarios.fecha_registro`.
* **`descuentos`**:
  *   `descuentos.fecha_registro`: Generada entre `SIMULATION_START_DATE` y `SIMULATION_END_DATE`.
  *   `descuentos.fecha_actualizacion`: Inicialmente generada poco después de `descuentos.fecha_registro`.
  *   `descuentos.fecha_inicio`: Debe ser `>= descuentos.fecha_registro`.
    * Ej: `get_random_datetime(min_date=descuentos.fecha_registro, max_date=SIMULATION_END_DATE)`
      *   `descuentos.fecha_fin`: Debe ser `>= descuentos.fecha_inicio`.
    * Ej: `get_random_datetime(min_date=descuentos.fecha_inicio, max_date=SIMULATION_END_DATE)`

2. **Entidades Dependientes de Primer Nivel**

* **`productos`** (Depende de: `proveedores` opcionalmente):
  *   `min_fecha_base_producto = SIMULATION_START_DATE`. Si el producto tiene un `proveedor_id`, entonces
  `min_fecha_base_producto = max(min_fecha_base_producto, proveedor_asociado.fecha_registro)`.
  *   `productos.fecha_registro`: `>= min_fecha_base_producto`.
  *   `productos.fecha_actualizacion`: Inicialmente `>= productos.fecha_registro`.
* **`inventario`** (Depende de: `productos`):
  *   `inventario.fecha_registro`: `>= producto_asociado.fecha_registro`.
  *   `inventario.fecha_actualizacion`: Inicialmente `>= inventario.fecha_registro`.

3. **Entidades Transaccionales y de Interacción del Usuario**

* **`carrito`** (Depende de: `usuarios`, `productos`):
  *   `min_fecha_base_carrito = max(usuario_asociado.fecha_registro, producto_asociado.fecha_registro)`.
  *   `carrito.fecha_registro`: `>= min_fecha_base_carrito`.
  *   `carrito.fecha_actualizacion`: Inicialmente `>= carrito.fecha_registro`.
* **`localizacion_pedido`** (Depende de: `usuarios`):
   *   `localizacion_pedido.fecha_registro`: `>= usuario_asociado.fecha_registro`.
   *   `localizacion_pedido.fecha_actualizacion`: Inicialmente `>= localizacion_pedido.fecha_registro`.* **`pedidos`** (Depende de: `usuarios`, `localizacion_pedido`, `productos` [vía `detalle_pedido`], `descuentos`
  opcionalmente):
  *
  `min_fecha_base_pedido = max(usuario_asociado.fecha_registro, localizacion_asociada.fecha_registro, max(p.fecha_registro for p in productos_en_el_pedido))`.
  *   `max_fecha_permitida_pedido = SIMULATION_END_DATE`.
  * Si se aplica un `descuento_aplicado`:
    *
    `min_fecha_base_pedido = max(min_fecha_base_pedido, descuento_aplicado.fecha_registro, descuento_aplicado.fecha_inicio)`.
    * `max_fecha_permitida_pedido = min(max_fecha_permitida_pedido, descuento_aplicado.fecha_fin)`.
      *   `pedidos.fecha_registro`: Debe estar entre `min_fecha_base_pedido` y `max_fecha_permitida_pedido`.
      *   `pedidos.fecha_actualizacion`: Inicialmente `>= pedidos.fecha_registro` (ej. para estado 'Pendiente').
* **`detalle_pedido`** (Depende de: `pedidos`, `productos`):
  *   `detalle_pedido.fecha_registro`: Generalmente igual a `pedido_asociado.fecha_registro`. Debe ser
  `>= max(pedido_asociado.fecha_registro, producto_asociado.fecha_registro)`.
  *   `detalle_pedido.fecha_actualizacion`: Inicialmente `>= detalle_pedido.fecha_registro`.

4. **Eventos Posteriores, Seguimiento y Auditorías**

* **Regla General para Actualizaciones y Auditorías:**
  Cuando una entidad es actualizada (ej. cambio de estado de un pedido, actualización de precio de producto):
  1. Se obtiene la `fecha_actualizacion_anterior` de la entidad.
  2. Se genera una `nueva_fecha_actualizacion` usando
  `generate_subsequent_update_datetime(previous_update_datetime=fecha_actualizacion_anterior)`.
  3. La entidad se actualiza con la `nueva_fecha_actualizacion`.
  4. El registro de auditoría correspondiente (`auditoria_usuarios`, `auditoria_productos`, `auditoria_inventario`,
  `auditoria_pedidos`) se crea con `fecha_cambio = nueva_fecha_actualizacion`.

* **`auditoria_usuarios`**:
  *   `auditoria_usuarios.fecha_cambio`: Corresponde a la `usuarios.fecha_actualizacion` cuando el estado del usuario
  cambió. Debe ser `> usuarios.fecha_registro` del usuario afectado.
* **`auditoria_productos`**:
  *   `auditoria_productos.fecha_cambio`: Corresponde a la `productos.fecha_actualizacion` cuando el precio o estado del
  producto cambió. Debe ser `> productos.fecha_registro` del producto afectado.
* **`auditoria_inventario`**:
  *   `auditoria_inventario.fecha_cambio`: Corresponde a la `inventario.fecha_actualizacion` cuando la cantidad
  disponible cambió. Debe ser `> inventario.fecha_registro` del inventario afectado.
* **`auditoria_pedidos`**:
  *   `auditoria_pedidos.fecha_cambio`: Corresponde a la `pedidos.fecha_actualizacion` cuando el estado del pedido
  cambió. Debe ser `> pedidos.fecha_registro` del pedido afectado.

* **`envios`** (Depende de: `pedidos`):
  *   `min_fecha_base_envio = pedido_asociado.fecha_actualizacion` (correspondiente al momento en que el pedido está
  listo para ser enviado, ej., estado 'Procesando' o cuando se actualiza a 'Enviado').
  *   `envios.fecha_registro`: `>= min_fecha_base_envio`.
  *   `envios.fecha_actualizacion`: Inicialmente `>= envios.fecha_registro`.
  *   `envios.fecha_envio` (si se establece): `>= envios.fecha_registro`.
  *   `envios.fecha_entrega_estimada` (si se establece): `>= envios.fecha_envio` (si `fecha_envio` existe).
  *   `envios.fecha_entrega_real` (si se establece): `>= envios.fecha_envio` (si `fecha_envio` existe).

* **`comentarios`** (Depende de: `usuarios`, `productos`; lógicamente ocurre después de que un usuario recibe un
  producto de un pedido):
  *   `min_fecha_base_comentario = max(usuario_asociado.fecha_registro, producto_asociado.fecha_registro)`.
  * Para mayor realismo, `min_fecha_base_comentario` debería ser `>= envio_asociado.fecha_entrega_real` (si existe) o
  `>= pedido_asociado.fecha_actualizacion` (cuando el pedido fue 'Entregado').
  *   `comentarios.fecha_registro`: `>= min_fecha_base_comentario`.
  *   `comentarios.fecha_actualizacion`: Inicialmente `>= comentarios.fecha_registro`.

* **`historial_descuentos`** (Depende de: `usuarios`, `descuentos`; asociado a un `pedidos` donde se usó el descuento):
  *   `historial_descuentos.fecha_registro`: Debería ser igual o muy cercana a `pedido_asociado.fecha_registro`.
  * Debe cumplir:
  `descuento_asociado.fecha_inicio <= historial_descuentos.fecha_registro <= descuento_asociado.fecha_fin`.
  * También:
  `historial_descuentos.fecha_registro >= max(usuario_asociado.fecha_registro, descuento_asociado.fecha_registro)`.
  *   `historial_descuentos.fecha_actualizacion`: Inicialmente `>= historial_descuentos.fecha_registro`.

* **`historial_metodos_envio`** (Depende de: `usuarios`; puede estar lógicamente conectado a `envios`):
  *   `min_fecha_base_hist_envio = usuario_asociado.fecha_registro`.
  * Si se considera que este historial se genera a partir de un envío concreto:
  `min_fecha_base_hist_envio = max(min_fecha_base_hist_envio, envio_asociado.fecha_registro)`.
  *   `historial_metodos_envio.fecha_registro`: `>= min_fecha_base_hist_envio`.
  *   `historial_metodos_envio.fecha_actualizacion`: Inicialmente `>= historial_metodos_envio.fecha_registro`.

Este enfoque paso a paso, respetando las dependencias y utilizando las utilidades de fecha, permitirá generar un
conjunto de datos coherente y realista para la simulación.

---

### Código para obtener los datos de envíos y localización de pedidos

```sql
SELECT lp.direccion_1, lp.ciudad, lp.departamento
FROM envios e
       JOIN pedidos p ON e.pedido_id = p.id
       JOIN localizacion_pedido lp ON p.id_localizacion = lp.id
ORDER BY e.pedido_id;
```

### Código para eliminar datos de la base de datos

```sql
DELETE FROM pedidos;
ALTER TABLE pedidos AUTO_INCREMENT = 1;

DELETE FROM auditoria_pedidos;
ALTER TABLE auditoria_pedidos AUTO_INCREMENT = 1;

DELETE FROM auditoria_usuarios;
ALTER TABLE auditoria_usuarios AUTO_INCREMENT = 1;

DELETE FROM usuarios;
ALTER TABLE usuarios AUTO_INCREMENT = 1;

DELETE FROM proveedores;
ALTER TABLE proveedores AUTO_INCREMENT = 1;

DELETE FROM auditoria_productos;
ALTER TABLE auditoria_productos AUTO_INCREMENT = 1;

DELETE FROM productos;
ALTER TABLE productos AUTO_INCREMENT = 1;

DELETE FROM auditoria_inventario;
ALTER TABLE auditoria_inventario AUTO_INCREMENT = 1;

DELETE FROM inventario;
ALTER TABLE inventario AUTO_INCREMENT = 1;

DELETE FROM localizacion_pedido;
ALTER TABLE localizacion_pedido AUTO_INCREMENT = 1;

DELETE FROM detalle_pedido;
ALTER TABLE detalle_pedido AUTO_INCREMENT = 1;

DELETE FROM auditoria_pedidos;
ALTER TABLE auditoria_pedidos AUTO_INCREMENT = 1;

DELETE FROM descuentos;
ALTER TABLE descuentos AUTO_INCREMENT = 1;

DELETE FROM historial_descuentos;
ALTER TABLE historial_descuentos AUTO_INCREMENT = 1;

DELETE FROM carrito;
ALTER TABLE carrito AUTO_INCREMENT = 1;

DELETE FROM comentarios;
ALTER TABLE comentarios AUTO_INCREMENT = 1;

DELETE FROM envios;
ALTER TABLE envios AUTO_INCREMENT = 1;

DELETE FROM historial_metodos_envio;
ALTER TABLE historial_metodos_envio AUTO_INCREMENT = 1;
```
```sql
-- amaluz
DELETE FROM pedido;
ALTER TABLE pedido AUTO_INCREMENT = 1;

DELETE FROM detalle_pedido;
ALTER TABLE detalle_pedido AUTO_INCREMENT = 1;

DELETE FROM empleado;
ALTER TABLE empleado AUTO_INCREMENT = 1;

DELETE FROM proveedor;
ALTER TABLE proveedor AUTO_INCREMENT = 1;

DELETE FROM productos;
ALTER TABLE productos AUTO_INCREMENT = 1;

DELETE FROM cliente;
ALTER TABLE cliente AUTO_INCREMENT = 1;

DELETE FROM envio;
ALTER TABLE envio AUTO_INCREMENT = 1;

DELETE FROM calificacion;
ALTER TABLE calificacion AUTO_INCREMENT = 1;

DELETE FROM inventario;
ALTER TABLE inventario AUTO_INCREMENT = 1;

DELETE FROM auditoria_inventario;
ALTER TABLE auditoria_inventario AUTO_INCREMENT = 1;
```