Claro, aquí tienes una explicación detallada de cada trigger implementado en tu archivo `db/schema.sql`:

**Triggers para Gestión de Inventario y Subtotales**

1.  **`trg_detalle_pedido_after_insert`**
    *   **Tabla:** `detalle_pedido`
    *   **Evento:** `AFTER INSERT` (Se ejecuta después de insertar una nueva fila)
    *   **Propósito:** Decrementar automáticamente la cantidad disponible de un producto en el inventario cuando 
        se añade un nuevo artículo a un pedido.
    *   **Lógica:** Cuando se inserta una fila en `detalle_pedido`, este trigger actualiza la tabla `inventario`, 
        restando la cantidad (`NEW.cantidad`) del producto (`NEW.producto_id`) recién añadido de la
        `cantidad_disponible`. Asume que un pedido recién creado no estará en un estado final como 
        'Cancelado' o 'Reembolsado'. La actualización en `inventario` disparará a su vez el trigger 
        `trg_auditoria_inventario_cantidad`.

2.  **`trg_detalle_pedido_after_delete`**
    *   **Tabla:** `detalle_pedido`
    *   **Evento:** `AFTER DELETE` (Se ejecuta después de eliminar una fila)
    *   **Propósito:** Incrementar automáticamente la cantidad disponible de un producto en el inventario si se 
        elimina un artículo de un detalle de pedido (por ejemplo, si se cancela un pedido antes de ser enviado).
    *   **Lógica:** Antes de actualizar, consulta el `estado_pedido` en la tabla `pedidos` asociada al detalle
        eliminado (`OLD.pedido_id`). Si el estado del pedido *no* es 'Entregado' ni 'Reembolsado',
        actualiza la tabla `inventario`, sumando la cantidad del artículo eliminado (`OLD.cantidad`)
        a la `cantidad_disponible` del producto (`OLD.producto_id`). Esto devuelve el stock. La actualización
        en `inventario` disparará el trigger `trg_auditoria_inventario_cantidad`.

3.  **`trg_detalle_pedido_after_update`**
    *   **Tabla:** `detalle_pedido`
    *   **Evento:** `AFTER UPDATE` (Se ejecuta después de actualizar una fila)
    *   **Propósito:** Ajustar la cantidad disponible en el inventario si se modifica la cantidad de un producto
        en un detalle de pedido existente.
    *   **Lógica:** Primero verifica si la cantidad ha cambiado (`OLD.cantidad <> NEW.cantidad`). Si cambió, 
        consulta el `estado_pedido` del pedido asociado. Si el estado *no* es 'Entregado', 'Reembolsado' o 
        'Cancelado' (estados donde el stock ya no debería fluctuar por cambios en el detalle), actualiza 
        `inventario.cantidad_disponible`. El ajuste se calcula sumando la cantidad antigua (`OLD.cantidad`)
        y restando la nueva (`NEW.cantidad`), reflejando la diferencia neta en el stock. La actualización en
        `inventario` disparará el trigger `trg_auditoria_inventario_cantidad`.

4.  **`trg_detalle_pedido_before_insert`**
    *   **Tabla:** `detalle_pedido`
    *   **Evento:** `BEFORE INSERT` (Se ejecuta antes de insertar una nueva fila)
    *   **Propósito:** Calcular automáticamente el campo `subtotal` antes de guardar un nuevo detalle de pedido.
    *   **Lógica:** Establece el valor de `NEW.subtotal` como el producto de `NEW.cantidad` y 
        `NEW.precio_unitario`. Esto asegura que el subtotal sea correcto sin necesidad de calcularlo en la aplicación.

5.  **`trg_detalle_pedido_before_update`**
    *   **Tabla:** `detalle_pedido`
    *   **Evento:** `BEFORE UPDATE` (Se ejecuta antes de actualizar una fila)
    *   **Propósito:** Recalcular automáticamente el campo `subtotal` si la cantidad o el precio unitario cambian
        durante una actualización.
    *   **Lógica:** Verifica si `OLD.cantidad` es diferente de `NEW.cantidad` o si `OLD.precio_unitario` es 
        diferente de `NEW.precio_unitario`. Si alguno de los dos cambió, recalcula `NEW.subtotal` como
        `NEW.cantidad * NEW.precio_unitario`.

**Triggers para Auditoría**

6.  **`trg_auditoria_usuarios_estado`**
    *   **Tabla:** `usuarios`
    *   **Evento:** `AFTER UPDATE`
    *   **Propósito:** Registrar un historial de cambios en el estado de un usuario.
    *   **Lógica:** Si el valor del campo `estado` ha cambiado (`OLD.estado <> NEW.estado`), inserta un nuevo registro
        en la tabla `auditoria_usuarios`, guardando el `usuario_id`, el `estado_anterior` (`OLD.estado`),
        el `estado_nuevo` (`NEW.estado`) y la fecha del cambio.

7.  **`trg_auditoria_productos_cambios`**
    *   **Tabla:** `productos`
    *   **Evento:** `AFTER UPDATE`
    *   **Propósito:** Registrar un historial de cambios en el precio de venta o el estado de un producto.
    *   **Lógica:** Si el `precio_venta` o el `estado` del producto han cambiado 
        (`OLD.precio_venta <> NEW.precio_venta OR OLD.estado <> NEW.estado`), inserta un nuevo registro 
        en `auditoria_productos`, guardando el `producto_id`, el precio anterior y nuevo,
        el estado anterior y nuevo, y la fecha del cambio.

8.  **`trg_auditoria_inventario_cantidad`**
    *   **Tabla:** `inventario`
    *   **Evento:** `AFTER UPDATE`
    *   **Propósito:** Registrar un historial de cambios en la cantidad disponible de un producto en el inventario.
    *   **Lógica:** Si la `cantidad_disponible` ha cambiado (`OLD.cantidad_disponible <> NEW.cantidad_disponible`),
        inserta un nuevo registro en `auditoria_inventario`, guardando el `producto_id`,
        la cantidad anterior y nueva, y la fecha del cambio. Este trigger es activado indirectamente
        por los triggers de gestión de inventario en `detalle_pedido`.

9.  **`trg_auditoria_pedidos_estado`**
    *   **Tabla:** `pedidos`
    *   **Evento:** `AFTER UPDATE`
    *   **Propósito:** Registrar un historial de cambios en el estado de un pedido.
    *   **Lógica:** Si el `estado_pedido` ha cambiado (`OLD.estado_pedido <> NEW.estado_pedido`),
        inserta un nuevo registro en `auditoria_pedidos`, guardando el `pedido_id`,
        el estado anterior y nuevo, y la fecha del cambio.