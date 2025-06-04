-- --- Triggers para Auditoría ---

-- Trigger para auditoría de cambios en cantidad disponible de inventario
DELIMITER $$
CREATE TRIGGER trg_auditoria_inventario_cantidad
    AFTER UPDATE
    ON inventario
    FOR EACH ROW
BEGIN
    -- Auditar cambios en cantidad_disponible, que es la relevante para ventas
    IF OLD.cantidad_disponible <> NEW.cantidad_disponible THEN
        INSERT INTO auditoria_inventario (id_producto, cantidad_anterior, cantidad_nueva, fecha_registro)
        VALUES (NEW.id_producto, OLD.cantidad_disponible, NEW.cantidad_disponible,
                NOW());
    END IF;
END$$
DELIMITER ;
