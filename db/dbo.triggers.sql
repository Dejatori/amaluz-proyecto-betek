-- --- Triggers para Auditoría ---

-- Trigger para auditoría de cambios de estado en usuarios
DELIMITER $$
CREATE TRIGGER trg_auditoria_usuarios_estado
    AFTER UPDATE
    ON usuarios
    FOR EACH ROW
BEGIN
    IF OLD.estado <> NEW.estado THEN
        INSERT INTO auditoria_usuarios (usuario_id, estado_anterior, estado_nuevo, fecha_cambio)
        VALUES (NEW.id, OLD.estado, NEW.estado, NEW.fecha_actualizacion);
    END IF;
END$$
DELIMITER ;

-- Trigger para auditoría de cambios de precio o estado en productos
DELIMITER $$
CREATE TRIGGER trg_auditoria_productos_cambios
    AFTER UPDATE
    ON productos
    FOR EACH ROW
BEGIN
    -- Solo auditar si cambia el precio de venta o el estado
    IF OLD.precio_venta <> NEW.precio_venta OR OLD.estado <> NEW.estado THEN
        INSERT INTO auditoria_productos (producto_id, precio_anterior, precio_nuevo, estado_anterior, estado_nuevo,
                                         fecha_cambio)
        VALUES (NEW.id, OLD.precio_venta, NEW.precio_venta, OLD.estado,
                NEW.estado, NEW.fecha_actualizacion);
    END IF;
END$$
DELIMITER ;

-- Trigger para auditoría de cambios en cantidad disponible de inventario
DELIMITER $$
CREATE TRIGGER trg_auditoria_inventario_cantidad
    AFTER UPDATE
    ON inventario
    FOR EACH ROW
BEGIN
    -- Auditar cambios en cantidad_disponible, que es la relevante para ventas
    IF OLD.cantidad_disponible <> NEW.cantidad_disponible THEN
        INSERT INTO auditoria_inventario (producto_id, cantidad_anterior, cantidad_nueva, fecha_cambio)
        VALUES (NEW.producto_id, OLD.cantidad_disponible, NEW.cantidad_disponible,
                NEW.fecha_actualizacion);
    END IF;
END$$
DELIMITER ;

-- Trigger para auditoría de cambios de estado en pedidos
DELIMITER $$
CREATE TRIGGER trg_auditoria_pedidos_estado
    AFTER UPDATE
    ON pedidos
    FOR EACH ROW
BEGIN
    IF OLD.estado_pedido <> NEW.estado_pedido THEN
        INSERT INTO auditoria_pedidos (pedido_id, estado_anterior, estado_nuevo, fecha_cambio)
        VALUES (NEW.id, OLD.estado_pedido, NEW.estado_pedido,
                NEW.fecha_actualizacion);
    END IF;
END$$
DELIMITER ;

-- --- Fin Triggers para Auditoría ---