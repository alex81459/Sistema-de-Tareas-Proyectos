USE tareas_proyectos;

ALTER TABLE tareas
    ADD COLUMN IF NOT EXISTS asignado_a_usuario_id INT NULL AFTER proyecto_id,
    ADD INDEX idx_tareas_asignado_a_usuario_id (asignado_a_usuario_id),
    ADD CONSTRAINT fk_tareas_asignado_a_usuario
        FOREIGN KEY (asignado_a_usuario_id) REFERENCES usuarios (id)
        ON DELETE SET NULL;
