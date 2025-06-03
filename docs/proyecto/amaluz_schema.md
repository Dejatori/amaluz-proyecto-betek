# Esquema de la base de datos Amaluz

## Entidades y Atributos

### Entidad `EMPLEADO`

-   `id_empleado` (PK, INT, AUTO_INCREMENT)
-   `nombre` (VARCHAR(255), NOT NULL)
-   `correo` (VARCHAR(255), NOT NULL, UNIQUE)
-   `contraseña` (VARCHAR(255), NOT NULL)
-   `telefono` (VARCHAR(20), NOT NULL)
-   `fecha_nacimiento` (DATE, NOT NULL)
-   `genero` (ENUM('masculino', 'femenino', 'otro'), NOT NULL)
-   `tipo_usuario` (ENUM('propietario', 'administrador', 'vendedor'), NOT NULL)
-   `estado` (ENUM('activo', 'inactivo', 'eliminado'), NOT NULL, DEFAULT 'activo')
-   `fecha_registro` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP)

**Reglas de Negocio:**

-   El campo `nombre` no puede estar vacío.
-   El campo `correo` debe ser único y tener un formato válido.
-   El campo `contraseña` no puede estar vacío y debe almacenarse de forma segura (ej. hasheada).
-   El campo `telefono` no puede estar vacío.
-   El campo `fecha_nacimiento` debe ser una fecha válida.
-   El campo `genero` debe ser uno de los valores definidos: ‘masculino’, ‘femenino’, ‘otro’.
-   El campo `tipo_usuario` debe ser uno de los valores definidos: ‘propietario’, ‘administrador’, ‘vendedor’.
-   El campo `estado` debe ser uno de los valores definidos: ‘activo’, ‘inactivo’, ‘eliminado’. Por defecto es ‘activo’.
-   El campo `fecha_registro` se establece automáticamente al crear un nuevo empleado.

### Entidad `PROVEEDOR`

-   `id_proveedor` (PK, INT, AUTO_INCREMENT)
-   `nombre` (VARCHAR(255), NOT NULL)
-   `descripcion` (TEXT, NOT NULL)
-   `telefono` (VARCHAR(20), NOT NULL)
-   `direccion` (VARCHAR(255), NOT NULL)
-   `fecha_registro` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP)

**Reglas de Negocio:**

-   Los campos `nombre`, `descripcion`, `telefono` y `direccion` no pueden estar vacíos.
-   El campo `fecha_registro` se establece automáticamente al crear un nuevo proveedor.

### Entidad `PRODUCTOS`

-   `id_producto` (PK, INT, AUTO_INCREMENT)
-   `nombre` (VARCHAR(255), NOT NULL)
-   `precio_venta` (DECIMAL(10, 2), NOT NULL, CHECK (`precio_venta` >= 0))
-   `categoria` (ENUM('Velas Aromáticas', 'Velas Decorativas', 'Velas Artesanales', 'Velas Personalizadas', 'Velas de Recordatorio'), NOT NULL)
-   `fragancia` (ENUM('Lavanda', 'Rosa', 'Cítricos', 'Vainilla', 'Chocolate', 'Eucalipto', 'Menta', 'Canela', 'Café', 'Tropical', 'Jazmín', 'Bebé', 'Sándalo', 'Pino', 'Naturaleza', 'Sofe', 'Cítricos Frescos', 'Frutos Rojos', 'Frutos Amarillos','Romero', 'Especias', 'Chicle', 'Coco', 'Tabaco & Chanelle'), NOT NULL)
-   `periodo_garantia` (INT, NOT NULL, CHECK (`periodo_garantia` >= 0))
-   `id_proveedor` (FK, INT, NOT NULL)
-   `fecha_registro` (DATETIME, DEFAULT CURRENT_TIMESTAMP)

**Reglas de Negocio:**

-   El campo `nombre` no puede estar vacío.
-   El campo `precio_venta` debe ser un valor numérico no negativo.
-   El campo `categoria` debe ser uno de los valores definidos.
-   El campo `fragancia` debe ser uno de los valores definidos.
-   El campo `periodo_garantia` debe ser un número entero no negativo (en días).
-   El campo `id_proveedor` debe referenciar a un proveedor existente en la tabla `PROVEEDOR`.
-   El campo `fecha_registro` se establece automáticamente al crear un nuevo producto (si no se especifica).

### Entidad `CLIENTE`

-   `id_cliente` (PK, INT, AUTO_INCREMENT)
-   `nombre` (VARCHAR(255), NOT NULL)
-   `telefono` (VARCHAR(20), NOT NULL)
-   `correo` (VARCHAR(255), NOT NULL, UNIQUE)
-   `fecha_nacimiento` (DATE, NOT NULL)
-   `fecha_registro` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP)

**Reglas de Negocio:**

-   Los campos `nombre`, `telefono`, `correo` y `fecha_nacimiento` no pueden estar vacíos.
-   El campo `correo` debe ser único y tener un formato válido.
-   El campo `fecha_nacimiento` debe ser una fecha válida.
-   El campo `fecha_registro` se establece automáticamente al crear un nuevo cliente.

### Entidad `PEDIDO`

-   `id_pedido` (PK, INT, AUTO_INCREMENT)
-   `id_cliente` (FK, INT, NOT NULL)
-   `metodo_pago` (ENUM('Tarjeta de Crédito', 'Transferencia Bancaria', 'PSE'), NOT NULL)
-   `costo_total` (DECIMAL(10, 2), NOT NULL, CHECK (`costo_total` >= 0))
-   `estado` (ENUM('pendiente', 'procesando', 'enviado', 'entregado', 'cancelado', 'reembolsado'), NOT NULL, DEFAULT 'pendiente')
-   `fecha_pedido` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP)

**Reglas de Negocio:**

-   El campo `id_cliente` debe referenciar a un cliente existente en la tabla `CLIENTE`.
-   El campo `metodo_pago` debe ser uno de los valores definidos.
-   El campo `costo_total` debe ser un valor numérico no negativo.
-   El campo `estado` debe ser uno de los valores definidos. Por defecto es ‘pendiente’.
-   El campo `fecha_pedido` se establece automáticamente al crear un nuevo pedido.

### Entidad `DETALLE_PEDIDO`

-   `id_detalle` (PK, INT, AUTO_INCREMENT)
-   `id_pedido` (FK, INT, NOT NULL)
-   `id_producto` (FK, INT, NOT NULL)
-   `cantidad` (INT, NOT NULL, CHECK (`cantidad` > 0))
-   `precio_unitario` (DECIMAL(10, 2), NOT NULL, CHECK (`precio_unitario` >= 0))
-   `subtotal` (DECIMAL(10, 2), NOT NULL, CHECK (`subtotal` >= 0))
-   `fecha_venta` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP)

**Reglas de Negocio:**

-   El campo `id_pedido` debe referenciar a un pedido existente en la tabla `PEDIDO`.
-   El campo `id_producto` debe referenciar a un producto existente en la tabla `PRODUCTOS`.
-   El campo `cantidad` debe ser un número entero mayor que 0.
-   El campo `precio_unitario` debe ser un valor numérico no negativo.
-   El campo `subtotal` debe ser un valor numérico no negativo (generalmente `cantidad * precio_unitario`).
-   El campo `fecha_venta` se establece automáticamente al crear un nuevo detalle de pedido.

### Entidad `ENVIO`

-   `id_envio` (PK, INT, AUTO_INCREMENT)
-   `id_pedido` (FK, INT, NOT NULL)
-   `empresa_envio` (VARCHAR(255), NOT NULL)
-   `referencia_emp_envio` (VARCHAR(255), NOT NULL)
-   `costo_envio` (DECIMAL(10, 2), NOT NULL, CHECK (`costo_envio` >= 0))
-   `direccion` (VARCHAR(255), NOT NULL)
-   `ciudad` (VARCHAR(100), NOT NULL)
-   `departamento` (VARCHAR(100), NOT NULL)
-   `estado_envio` (ENUM('pendiente', 'en tránsito', 'entregado', 'devuelto', 'incidencia'), NOT NULL, DEFAULT 'pendiente')
-   `fecha_envio` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP)
-   `fecha_estimada_entrega` (DATETIME, NOT NULL)
-   `fecha_entrega_real` (DATETIME, DEFAULT NULL)

**Reglas de Negocio:**

-   El campo `id_pedido` debe referenciar a un pedido existente en la tabla `PEDIDO`.
-   Los campos `empresa_envio`, `referencia_emp_envio`, `direccion`, `ciudad` y `departamento` no pueden estar vacíos.
-   El campo `costo_envio` debe ser un valor numérico no negativo.
-   El campo `estado_envio` debe ser uno de los valores definidos. Por defecto es ‘pendiente’.
-   El campo `fecha_envio` se establece automáticamente al crear un nuevo envío.
-   El campo `fecha_estimada_entrega` no puede estar vacío.
-   El campo `fecha_entrega_real` puede ser NULL hasta que se confirme la entrega.

### Entidad `CALIFICACION`

-   `id_calificacion` (PK, INT, AUTO_INCREMENT)
-   `id_cliente` (FK, INT, NOT NULL)
-   `id_producto` (FK, INT, NOT NULL)
-   `calificacion` (INT, NOT NULL, CHECK (`calificacion` >= 1 AND `calificacion` <= 5))
-   `fecha_calificacion` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP)

**Reglas de Negocio:**

-   El campo `id_cliente` debe referenciar a un cliente existente en la tabla `CLIENTE`.
-   El campo `id_producto` debe referenciar a un producto existente en la tabla `PRODUCTOS`.
-   El campo `calificacion` debe ser un número entero entre 1 y 5.
-   El campo `fecha_calificacion` se establece automáticamente al crear una nueva calificación.

### Entidad `INVENTARIO`

-   `id_inventario` (PK, INT, AUTO_INCREMENT)
-   `id_producto` (FK, INT, NOT NULL, UNIQUE)
-   `cantidad_total` (INT, NOT NULL, CHECK (`cantidad_total` >= 0))
-   `cantidad_disponible` (INT, NOT NULL, CHECK (`cantidad_disponible` >= 0))
-   `fecha_registro` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP)
-   CHECK (`cantidad_disponible` <= `cantidad_total`)

**Reglas de Negocio:**

-   El campo `id_producto` debe referenciar a un producto existente en la tabla `PRODUCTOS` y debe ser único (un registro de inventario por producto).
-   Los campos `cantidad_total` y `cantidad_disponible` deben ser números enteros no negativos.
-   La `cantidad_disponible` no puede ser mayor que la `cantidad_total`.
-   El campo `fecha_registro` se establece automáticamente al crear un nuevo registro de inventario.

### Entidad `AUDITORIA_INVENTARIO`

-   `id` (PK, INT, AUTO_INCREMENT)
-   `id_producto` (FK, INT, NOT NULL)
-   `cantidad_anterior` (INT, NOT NULL, CHECK (`cantidad_anterior` >= 0))
-   `cantidad_nueva` (INT, NOT NULL, CHECK (`cantidad_nueva` >= 0))
-   `fecha_registro` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP)

**Reglas de Negocio:**

-   Registra los cambios en las cantidades de inventario de los productos.
-   El campo `id_producto` debe referenciar a un producto existente en la tabla `PRODUCTOS`.
-   Los campos `cantidad_anterior` y `cantidad_nueva` deben ser números enteros no negativos, representando el stock antes y después del cambio.
-   El campo `fecha_registro` se establece automáticamente al crear un nuevo registro de auditoría.

## Relaciones y Cardinalidad

A continuación se describen las relaciones entre las entidades principales y su cardinalidad:

-   **`PROVEEDOR` (1) <-> `PRODUCTOS` (N) (Uno a Muchos):**
    Un proveedor puede suministrar múltiples productos. Un producto es suministrado por un proveedor.
    Si se elimina un proveedor, los productos asociados también se eliminarán (`ON DELETE CASCADE`).
-   **`CLIENTE` (1) <-> `PEDIDO` (N) (Uno a Muchos):**
    Un cliente puede realizar múltiples pedidos. Un pedido pertenece a un único cliente.
    Si se elimina un cliente, sus pedidos asociados también se eliminarán (`ON DELETE CASCADE`).
-   **`PEDIDO` (1) <-> `DETALLE_PEDIDO` (N) (Uno a Muchos):**
    Un pedido se compone de múltiples líneas de detalle, cada una correspondiente a un producto.
    Si se elimina un pedido, sus detalles asociados también se eliminarán (`ON DELETE CASCADE`).
-   **`PRODUCTOS` (1) <-> `DETALLE_PEDIDO` (N) (Uno a Muchos):**
    Un producto puede aparecer en las líneas de detalle de múltiples pedidos.
    Si se elimina un producto, las líneas de detalle de pedido asociadas también se eliminarán (`ON DELETE CASCADE`).
-   **`PEDIDO` (1) <-> `ENVIO` (N) (Uno a Muchos):**
    Un pedido puede tener uno o varios envíos asociados (aunque comúnmente es uno). Un envío pertenece a un único pedido.
    Si se elimina un pedido, sus envíos asociados también se eliminarán (`ON DELETE CASCADE`).
-   **`CLIENTE` (1) <-> `CALIFICACION` (N) (Uno a Muchos):**
    Un cliente puede realizar múltiples calificaciones sobre productos. Una calificación es realizada por un único cliente.
    Si se elimina un cliente, sus calificaciones asociadas también se eliminarán (`ON DELETE CASCADE`).
-   **`PRODUCTOS` (1) <-> `CALIFICACION` (N) (Uno a Muchos):**
    Un producto puede recibir múltiples calificaciones de diferentes clientes. Una calificación se refiere a un único producto.
    Si se elimina un producto, sus calificaciones asociadas también se eliminarán (`ON DELETE CASCADE`).
-   **`PRODUCTOS` (1) <-> `INVENTARIO` (1) (Uno a Uno):**
    Cada producto tiene exactamente una entrada en la tabla de inventario, gracias a la restricción `UNIQUE` en `id_producto`.
    Si se elimina un producto, su registro de inventario asociado también se eliminará (`ON DELETE CASCADE`).
-   **`PRODUCTOS` (1) <-> `AUDITORIA_INVENTARIO` (N) (Uno a Muchos):**
    Un producto puede tener múltiples registros de auditoría asociados a cambios en su inventario.
    Si se elimina un producto, sus registros de auditoría de inventario asociados también se eliminarán (`ON DELETE CASCADE`).