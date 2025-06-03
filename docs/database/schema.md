# Esquema de la base de datos

## Entidades y Atributos

### Entidad `usuarios`

- id (PK)
- nombre
- correo
- contrasena
- telefono
- fecha_nacimiento
- genero
- tipo_usuario
- estado
- fecha_registro
- fecha_actualizacion

**Reglas de Negocio:**

- El campo `correo` debe ser único y tener un formato válido.
- El campo `contrasena` debe tener al menos 8 caracteres, una letra mayúscula, una minúscula,
  un número y un carácter especial. Las contraseñas deben ser almacenadas de forma segura utilizando
  un algoritmo de hash (ejemplo: bcrypt).
- El campo `telefono` debe ser único y tener un formato válido.
- El campo `fecha_nacimiento` debe ser una fecha válida y no puede ser mayor a la actual.
- El campo `tipo_usuario` puede ser ‘Cliente’, ‘Administrador’ o ‘Vendedor’.
- El campo `estado` puede ser ‘Activo’, ‘Inactivo’, ‘Bloqueado’, ‘Eliminado’ o ‘Sin confirmar’.
- El campo `fecha_registro` se establecerá automáticamente al crear un nuevo usuario.
- El campo `fecha_actualizacion` se actualizará automáticamente al modificar un usuario.

### Entidad `auditoria_usuarios`

- id (PK)
- usuario_id (FK)
- estado_anterior
- estado_nuevo
- fecha_cambio

**Reglas de Negocio:**

- La auditoría de usuarios se registrará cada vez que cambie el estado de un usuario.
- El campo `estado_anterior` y `estado_nuevo` pueden ser ‘Activo’, ‘Inactivo’, ‘Bloqueado’, ‘Eliminado’
  o ‘Sin confirmar’.
- El campo `fecha_cambio` se establecerá automáticamente al crear un nuevo registro de auditoría.
- El campo `usuario_id` debe referirse a un usuario existente en la tabla `usuarios`.

### Entidad `proveedores`

- id (PK)
- nombre
- telefono
- direccion
- fecha_registro
- fecha_actualizacion

**Reglas de Negocio:**

- El campo `nombre` no puede estar vacío.
- El campo `telefono` no puede estar vacío.
- El campo `direccion` no puede estar vacío.
- El campo `fecha_registro` se establecerá automáticamente al crear un nuevo proveedor.
- El campo `fecha_actualizacion` se actualizará automáticamente al modificar un proveedor.

### Entidad `productos`

- id (PK)
- nombre
- descripcion
- precio_venta
- categoria
- peso
- dimensiones
- imagen_url
- fragancia
- periodo_garantia
- estado
- precio_proveedor
- proveedor_id (FK)
- fecha_registro
- fecha_actualizacion

**Reglas de Negocio:**

- El campo `nombre` no puede estar vacío.
- El campo `descripcion` no puede estar vacío.
- El campo `precio_venta` debe ser mayor que 0.
- El campo `precio_venta` debe ser mayor que `precio_proveedor`.
- El campo `categoria` debe ser uno de los valores definidos: ‘Velas Aromáticas’, ‘Velas Decorativas’, 
  ‘Velas Artesanales’, ‘Velas Personalizadas’, ‘Velas de Recordatorio’.
- El campo `peso` debe ser un valor decimal y se almacenará en gramos. Ejemplo: ‘1000,00’ para 1 kg.
- El campo `dimensiones` se almacenará como ‘Alto x Ancho x Profundidad’.en centímetros. Ejemplo: ‘10x20x30’.
- El campo `imagen_url` no puede estar vacío.
- El campo `fragancia` debe ser uno de los valores definidos: ‘Lavanda’, ‘Rosa’, ‘Cítricos’, ‘Vainilla’, 
  ‘Chocolate’, ‘Eucalipto’, ‘Menta’, ‘Canela’, ‘Café’, ‘Tropical’, ‘Jazmín’, ‘Bebé’, ‘Sándalo’, ‘Pino’, ‘Naturaleza’,
  ‘Sofe’, ‘Cítricos Frescos’, ‘Frutos Rojos’, ‘Frutos Amarillos’,‘Romero’, ‘Especias’, ‘Chicle’, ‘Coco’,
  ‘Tabaco & Chanelle’.
- El campo `periodo_garantia` se almacenará en días. El valor por defecto es 90 días.
- El campo `estado` puede ser ‘Activo’.o ‘Inactivo’. El valor por defecto es ‘Activo’.
- El campo `precio_proveedor` debe ser mayor que 0.
- El campo `proveedor_id` es una clave foránea que referencia a la tabla `proveedores`. Puede ser NULL.
- Si se elimina un proveedor, el campo `proveedor_id` de los productos asociados se establecerá en NULL 
  (ON DELETE SET NULL).
- El campo `fecha_registro` se establecerá automáticamente al crear un nuevo producto.
- El campo `fecha_actualizacion` se actualizará automáticamente al modificar un producto.

### Entidad `auditoria_productos`

- id (PK)
- producto_id (FK)
- precio_anterior
- precio_nuevo
- estado_anterior
- estado_nuevo
- fecha_cambio

**Reglas de Negocio:**

- La auditoría de productos se registrará cada vez que cambie el `precio_venta` o el `estado` de un producto.
- El campo `producto_id` debe referirse a un producto existente en la tabla `productos`.
- Los campos `precio_anterior` y `precio_nuevo` almacenarán los valores del `precio_venta` antes y después del cambio.
- Los campos `estado_anterior` y `estado_nuevo` pueden ser ‘Activo’.o ‘Inactivo’.
- El campo `fecha_cambio` se establecerá automáticamente al crear un nuevo registro de auditoría.
- Si se elimina un producto, los registros de auditoría asociados también se eliminarán (ON DELETE CASCADE).

### Entidad `inventario`

- id (PK)
- producto_id (FK, UNIQUE)
- cantidad_mano
- cantidad_disponible
- fecha_registro
- fecha_actualizacion

**Reglas de Negocio:**

- Cada producto solo puede tener una entrada en la tabla `inventario` (`producto_id` es único).
- El campo `cantidad_mano` representa la cantidad física total del producto. El valor por defecto es 0.
- El campo `cantidad_disponible` representa la cantidad disponible para la venta (puede ser menor que `cantidad_mano`
  debido a reservas). El valor por defecto es 0.
- El campo `producto_id` debe referirse a un producto existente en la tabla `productos`.
- Si se elimina un producto, su registro de inventario asociado también se eliminará (ON DELETE CASCADE).
- El campo `fecha_registro` se establecerá automáticamente al crear un nuevo registro de inventario.
- El campo `fecha_actualizacion` se actualizará automáticamente al modificar un registro de inventario.

### Entidad `auditoria_inventario`

- id (PK)
- producto_id (FK)
- cantidad_anterior
- cantidad_nueva
- fecha_cambio

**Reglas de Negocio:**

- La auditoría de inventario se registrará cada vez que cambie la `cantidad_disponible` de un producto 
  en la tabla `inventario`.
- El campo `producto_id` debe referirse a un producto existente en la tabla `productos`.
- Los campos `cantidad_anterior` y `cantidad_nueva` almacenarán los valores de `cantidad_disponible`
  antes y después del cambio.
- El campo `fecha_cambio` se establecerá automáticamente al crear un nuevo registro de auditoría.
- Si se elimina un producto, los registros de auditoría de inventario asociados también se eliminarán
  (ON DELETE CASCADE).

### Entidad `localizacion_pedido`

- id (PK)
- usuario_id (FK)
- direccion_1
- direccion_2
- ciudad
- departamento
- codigo_postal
- descripcion
- notas_entrega
- fecha_registro
- fecha_actualizacion

**Reglas de Negocio:**

- El campo `usuario_id` debe referirse a un usuario existente en la tabla `usuarios`.
- Los campos `direccion_1`, `ciudad`, `departamento` y `codigo_postal` no pueden estar vacíos.
- El campo `descripcion` puede usarse como un alias para la dirección (ej. ‘Casa’, ‘Oficina’).
- El campo `notas_entrega` permite añadir instrucciones adicionales para la entrega.
- Si se elimina un usuario, sus localizaciones de pedido asociadas también se eliminarán (ON DELETE CASCADE).
- El campo `fecha_registro` se establecerá automáticamente al crear una nueva localización.
- El campo `fecha_actualizacion` se actualizará automáticamente al modificar una localización.

### Entidad `pedidos`

- id (PK)
- usuario_id (FK)
- id_localizacion (FK)
- codigo_pedido
- costo_total
- metodo_pago
- estado_pedido
- fecha_registro
- fecha_actualizacion

**Reglas de Negocio:**

- El campo `usuario_id` debe referirse a un usuario existente en la tabla `usuarios`.
- El campo `id_localizacion` debe referirse a una localización existente en la tabla `localizacion_pedido`.
- El campo `codigo_pedido` debe ser único y no puede estar vacío. Se usa para el seguimiento del pedido.
- El campo `costo_total` no puede estar vacío y representa el monto final a pagar
  (incluye subtotales, envío, descuentos).
- El campo `metodo_pago` debe ser uno de los valores definidos: ‘Tarjeta de Crédito’, ‘Transferencia Bancaria’, ‘PSE’.
- El campo `estado_pedido` debe ser uno de los valores definidos: ‘Pendiente’, ‘Procesando’, ‘Enviado’, ‘Entregado’, 
  ‘Cancelado’, ‘Reembolsado’. El valor por defecto es ‘Pendiente’.
- No se permite eliminar un usuario si tiene pedidos asociados (ON DELETE RESTRICT).
- No se permite eliminar una localización si está asociada a algún pedido (ON DELETE RESTRICT).
- El campo `fecha_registro` se establecerá automáticamente al crear un nuevo pedido.
- El campo `fecha_actualizacion` se actualizará automáticamente al modificar un pedido.

### Entidad `detalle_pedido`

- id (PK)
- pedido_id (FK)
- producto_id (FK)
- cantidad
- precio_unitario
- subtotal
- fecha_registro
- fecha_actualizacion

**Reglas de Negocio:**

- El campo `pedido_id` debe referirse a un pedido existente en la tabla `pedidos`.
- El campo `producto_id` debe referirse a un producto existente en la tabla `productos`.
- El campo `cantidad` debe ser un número entero mayor que 0.
- El campo `precio_unitario` almacena el precio del producto en el momento de la compra y no puede estar vacío.
- El campo `subtotal` se calcula como `cantidad * precio_unitario` y no puede estar vacío.
- La combinación de `pedido_id` y `producto_id` debe ser única (un producto solo puede aparecer una vez por pedido).
- Si se elimina un pedido, sus detalles asociados también se eliminarán (ON DELETE CASCADE).
- No se permite eliminar un producto si está incluido en algún detalle de pedido (ON DELETE RESTRICT).
- El campo `fecha_registro` se establecerá automáticamente al crear un nuevo detalle de pedido.
- El campo `fecha_actualizacion` se actualizará automáticamente al modificar un detalle de pedido.

### Entidad `auditoria_pedidos`

- id (PK)
- pedido_id (FK)
- estado_anterior
- estado_nuevo
- fecha_cambio

**Reglas de Negocio:**

- La auditoría de pedidos se registrará cada vez que cambie el `estado_pedido` de un pedido.
- El campo `pedido_id` debe referirse a un pedido existente en la tabla `pedidos`.
- Los campos `estado_anterior` y `estado_nuevo` deben ser uno de los valores definidos para `pedidos.estado_pedido`.
- El campo `fecha_cambio` se establecerá automáticamente al crear un nuevo registro de auditoría.
- Si se elimina un pedido, los registros de auditoría asociados también se eliminarán (ON DELETE CASCADE).

### Entidad `descuentos`

- id (PK)
- codigo_descuento
- porcentaje
- fecha_inicio
- fecha_fin
- estado
- fecha_registro
- fecha_actualizacion

**Reglas de Negocio:**

- El campo `codigo_descuento` debe ser único y no puede estar vacío.
- El campo `porcentaje` debe ser un valor decimal entre 0 (exclusivo) y 100 (inclusivo).
- Los campos `fecha_inicio` y `fecha_fin` no pueden estar vacíos y definen el período de validez del descuento.
- El campo `estado` puede ser ‘Activo’.o ‘Inactivo’. El valor por defecto es ‘Activo’.
- El campo `fecha_registro` se establecerá automáticamente al crear un nuevo descuento.
- El campo `fecha_actualizacion` se actualizará automáticamente al modificar un descuento.

### Entidad `historial_descuentos`

- id (PK)
- usuario_id (FK)
- descuento_id (FK)
- fecha_registro
- fecha_actualizacion

**Reglas de Negocio:**

- Registra qué usuarios han utilizado qué descuentos.
- El campo `usuario_id` debe referirse a un usuario existente en la tabla `usuarios`.
- El campo `descuento_id` debe referirse a un descuento existente en la tabla `descuentos`.
- Si se elimina un usuario, su historial de descuentos asociado también se eliminará (ON DELETE CASCADE).
- Si se elimina un descuento, su historial asociado también se eliminará (ON DELETE CASCADE).
- El campo `fecha_registro` se establecerá automáticamente al crear un nuevo registro en el historial.
- El campo `fecha_actualizacion` se actualizará automáticamente al modificar un registro en el historial.

### Entidad `carrito`

- id (PK)
- usuario_id (FK)
- producto_id (FK)
- cantidad
- fecha_registro
- fecha_actualizacion

**Reglas de Negocio:**

- El campo `usuario_id` debe referirse a un usuario existente en la tabla `usuarios`.
- El campo `producto_id` debe referirse a un producto existente en la tabla `productos`.
- El campo `cantidad` debe ser un número entero mayor que 0.
- La combinación de `usuario_id` y `producto_id` debe ser única (un producto solo puede estar una vez en el 
  carrito de un usuario).
- Si se elimina un usuario, los elementos de su carrito asociado también se eliminarán (ON DELETE CASCADE).
- Si se elimina un producto, se eliminará de todos los carritos en los que aparezca (ON DELETE CASCADE).
- El campo `fecha_registro` se establecerá automáticamente al añadir un producto al carrito.
- El campo `fecha_actualizacion` se actualizará automáticamente al modificar la cantidad de un producto en el carrito.

### Entidad `comentarios`

- id (PK)
- usuario_id (FK)
- producto_id (FK)
- comentario
- calificacion
- fecha_registro
- fecha_actualizacion

**Reglas de Negocio:**

- El campo `usuario_id` debe referirse a un usuario existente en la tabla `usuarios`.
- El campo `producto_id` debe referirse a un producto existente en la tabla `productos`.
- El campo `comentario` no puede estar vacío.
- El campo `calificacion` debe ser un número entero entre 1 y 5 (inclusive). Puede ser NULL si no
  se proporciona calificación.
- Si se elimina un usuario, sus comentarios asociados también se eliminarán (ON DELETE CASCADE).
- Si se elimina un producto, sus comentarios asociados también se eliminarán (ON DELETE CASCADE).
- El campo `fecha_registro` se establecerá automáticamente al crear un nuevo comentario.
- El campo `fecha_actualizacion` se actualizará automáticamente al modificar un comentario.

### Entidad `envios`

- id (PK)
- pedido_id (FK, UNIQUE)
- empresa_envio
- numero_guia (UNIQUE)
- costo_envio
- fecha_envio
- fecha_entrega_estimada
- fecha_entrega_real
- estado_envio
- fecha_registro
- fecha_actualizacion

**Reglas de Negocio:**

- El campo `pedido_id` debe referirse a un pedido existente en la tabla `pedidos` y debe ser único (un envío por pedido).
- Los campos `empresa_envio` y `numero_guia` no pueden estar vacíos. Él `numero_guia` debe ser único.
- El campo `costo_envio` no puede ser negativo. El valor por defecto es 0,00.
- Los campos `fecha_envio`, `fecha_entrega_estimada` y `fecha_entrega_real` son opcionales (pueden ser NULL).
- El campo `estado_envio` debe ser uno de los valores definidos: ‘Pendiente’, ‘En tránsito’, ‘Entregado’,
  ‘Devuelto’, ‘Incidencia’. El valor por defecto es ‘Pendiente’.
- Si se elimina un pedido, la información de envío asociada también se eliminará (ON DELETE CASCADE).
- El campo `fecha_registro` se establecerá automáticamente al crear un nuevo registro de envío.
- El campo `fecha_actualizacion` se actualizará automáticamente al modificar un registro de envío.

### Entidad `historial_metodos_envio`

- id (PK)
- usuario_id (FK)
- empresa_envio
- costo_envio
- fecha_registro
- fecha_actualizacion

**Reglas de Negocio:**

- Registra información histórica o preferencias de envío por usuario (si aplica, revisar si esta tabla 
  es necesaria o si la información está en `envios`).
- El campo `usuario_id` debe referirse a un usuario existente en la tabla `usuarios`.
- El campo `empresa_envio` no puede estar vacío.
- El campo `costo_envio` no puede ser negativo.
- Si se elimina un usuario, su historial de métodos de envío asociado también se eliminará (ON DELETE CASCADE).
- El campo `fecha_registro` se establecerá automáticamente al crear un nuevo registro en el historial.
- El campo `fecha_actualizacion` se actualizará automáticamente al modificar un registro en el historial.

## Relaciones y Cardinalidad

A continuación se describen las relaciones entre las entidades principales y su cardinalidad:

-   **`usuarios` (1) <-> `auditoria_usuarios` (N) (Uno a Muchos):**
    Un usuario puede tener múltiples registros de auditoría asociados a cambios en su estado. Si se elimina un usuario,
    se eliminan sus registros de auditoría (`ON DELETE CASCADE`).
-   **`proveedores` (1) <-> `productos` (N) (Uno a Muchos):**
    Un proveedor puede suministrar múltiples productos. Un producto pertenece a un único proveedor 
    (o a ninguno, si `proveedor_id` es NULL). Si se elimina un proveedor, él `proveedor_id` en los productos 
    asociados se establece a NULL (`ON DELETE SET NULL`).
-   **`productos` (1) <-> `auditoria_productos` (N) (Uno a Muchos):**
    Un producto puede tener múltiples registros de auditoría asociados a cambios en su precio o estado. Si se elimina
    un producto, se eliminan sus registros de auditoría (`ON DELETE CASCADE`).
-   **`productos` (1) <-> `inventario` (1) (Uno a Uno):**
    Cada producto tiene exactamente una entrada en la tabla de inventario, gracias a la restricción `UNIQUE` en 
    `producto_id`. Si se elimina un producto, se elimina su registro de inventario (`ON DELETE CASCADE`).
-   **`productos` (1) <-> `auditoria_inventario` (N) (Uno a Muchos):**
    Un producto puede tener múltiples registros de auditoría asociados a cambios en su cantidad disponible en inventario.
    Si se elimina un producto, se eliminan sus registros de auditoría de inventario (`ON DELETE CASCADE`).
-   **`usuarios` (1) <-> `localizacion_pedido` (N) (Uno a Muchos):**
    Un usuario puede registrar múltiples direcciones (localizaciones) para sus pedidos. Si se elimina un usuario, 
    se eliminan sus localizaciones (`ON DELETE CASCADE`).
-   **`usuarios` (1) <-> `pedidos` (N) (Uno a Muchos):**
    Un usuario puede realizar múltiples pedidos. No se puede eliminar un usuario si tiene pedidos asociados 
    (`ON DELETE RESTRICT`).
-   **`localizacion_pedido` (1) <-> `pedidos` (N) (Uno a Muchos):**
    Una dirección (localización) puede ser utilizada en múltiples pedidos. No se puede eliminar una localización si 
    está asociada a algún pedido (`ON DELETE RESTRICT`).
-   **`pedidos` (1) <-> `detalle_pedido` (N) (Uno a Muchos):**
    Un pedido se compone de múltiples líneas de detalle, cada una correspondiente a un producto. Si se elimina un pedido,
    se eliminan sus detalles (`ON DELETE CASCADE`).
-   **`productos` (1) <-> `detalle_pedido` (N) (Uno a Muchos):**
    Un producto puede aparecer en las líneas de detalle de múltiples pedidos. No se puede eliminar un producto si está 
    incluido en algún detalle de pedido (`ON DELETE RESTRICT`).
-   **`pedidos` (1) <-> `auditoria_pedidos` (N) (Uno a Muchos):**
    Un pedido puede tener múltiples registros de auditoría asociados a cambios en su estado. Si se elimina un pedido, 
    se eliminan sus registros de auditoría (`ON DELETE CASCADE`).
-   **`usuarios` (1) <-> `historial_descuentos` (N) (Uno a Muchos):**
    Un usuario puede haber utilizado múltiples descuentos a lo largo del tiempo. Si se elimina un usuario, se elimina
    su historial de descuentos (`ON DELETE CASCADE`).
-   **`descuentos` (1) <-> `historial_descuentos` (N) (Uno a Muchos):**
    Un código de descuento puede ser utilizado por múltiples usuarios. Si se elimina un descuento, se elimina su 
    historial de uso (`ON DELETE CASCADE`).
-   **`usuarios` (1) <-> `carrito` (N) (Uno a Muchos):**
    Un usuario tiene un carrito de compras que puede contener múltiples productos (ítems). La restricción 
    `UNIQUE(usuario_id, producto_id)` asegura que cada producto aparezca solo una vez por carrito. Si se elimina un
    usuario, se elimina su carrito (`ON DELETE CASCADE`).
-   **`productos` (1) <-> `carrito` (N) (Uno a Muchos):**
    Un producto puede estar en los carritos de múltiples usuarios. Si se elimina un producto, se elimina de todos los 
    carritos (`ON DELETE CASCADE`).
-   **`usuarios` (1) <-> `comentarios` (N) (Uno a Muchos):**
    Un usuario puede escribir múltiples comentarios sobre productos. Si se elimina un usuario, se eliminan sus 
    comentarios (`ON DELETE CASCADE`).
-   **`productos` (1) <-> `comentarios` (N) (Uno a Muchos):**
    Un producto puede recibir múltiples comentarios de diferentes usuarios. Si se elimina un producto, se eliminan 
    sus comentarios (`ON DELETE CASCADE`).
-   **`pedidos` (1) <-> `envios` (1) (Uno a Uno):**
    Cada pedido tiene exactamente una entrada en la tabla de envíos, gracias a la restricción `UNIQUE` en `pedido_id`.
    Si se elimina un pedido, se elimina su información de envío (`ON DELETE CASCADE`).
-   **`usuarios` (1) <-> `historial_metodos_envio` (N) (Uno a Muchos):**
    Un usuario puede tener un historial asociado a múltiples métodos de envío (si esta tabla se usa para registrar 
    preferencias o usos pasados). Si se elimina un usuario, se elimina su historial (`ON DELETE CASCADE`).
-   **`usuarios` (1) <-> `historial_metodos_pago` (N) (Uno a Muchos):**
    Un usuario puede tener un historial asociado al uso de múltiples métodos de pago. Si se elimina un usuario, 
    se elimina su historial (`ON DELETE CASCADE`).
-   **`metodos_pago` (1) <-> `historial_metodos_pago` (N) (Uno a Muchos):**
    Un método de pago puede aparecer en el historial de múltiples usuarios. Si se elimina un método de pago, 
    se elimina su historial asociado (`ON DELETE CASCADE`).