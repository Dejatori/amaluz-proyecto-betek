-- --- Índices para Optimización ---

-- Índice en correo de usuarios para búsquedas rápidas y login
CREATE INDEX idx_usuarios_correo ON usuarios (correo);

-- Índice en categoría de productos para filtrar por categoría
CREATE INDEX idx_productos_categoria ON productos (categoria);

-- Índice en fragancia de productos para filtrar por fragancia
CREATE INDEX idx_productos_fragancia ON productos (fragancia);

-- Índice en estado de productos para filtrar productos activos/inactivos
CREATE INDEX idx_productos_estado ON productos (estado);

-- Índice en usuario_id de pedidos para buscar pedidos por usuario
CREATE INDEX idx_pedidos_usuario_id ON pedidos (usuario_id);

-- Índice en estado_pedido para filtrar pedidos por estado
CREATE INDEX idx_pedidos_estado ON pedidos (estado_pedido);

-- Índice en pedido_id de detalle_pedido para unir rápidamente con pedidos
CREATE INDEX idx_detalle_pedido_pedido_id ON detalle_pedido (pedido_id);

-- Índice en producto_id de detalle_pedido para análisis de ventas por producto
CREATE INDEX idx_detalle_pedido_producto_id ON detalle_pedido (producto_id);

-- Índice en usuario_id de carrito para obtener el carrito de un usuario
CREATE INDEX idx_carrito_usuario_id ON carrito (usuario_id);

-- Índice en producto_id de comentarios para buscar comentarios de un producto
CREATE INDEX idx_comentarios_producto_id ON comentarios (producto_id);

-- Índice en usuario_id de comentarios para buscar comentarios de un usuario
CREATE INDEX idx_comentarios_usuario_id ON comentarios (usuario_id);

-- Índice en numero_guia de envíos para búsquedas por guía
CREATE INDEX idx_envios_numero_guia ON envios (numero_guia);

-- Índice en estado_envio para filtrar envíos por estado
CREATE INDEX idx_envios_estado ON envios (estado_envio);
