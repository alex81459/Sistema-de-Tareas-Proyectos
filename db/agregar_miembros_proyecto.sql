USE tareas_proyectos;

CREATE TABLE IF NOT EXISTS miembros_proyecto (
    id INT NOT NULL AUTO_INCREMENT,
    proyecto_id INT NOT NULL,
    usuario_id INT NOT NULL,
    permiso VARCHAR(20) NOT NULL DEFAULT 'lectura',
    creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_miembro_proyecto_usuario UNIQUE (proyecto_id, usuario_id),
    CONSTRAINT fk_miembros_proyecto_proyecto
        FOREIGN KEY (proyecto_id) REFERENCES proyectos (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_miembros_proyecto_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        ON DELETE CASCADE,
    INDEX idx_miembros_proyecto_proyecto_id (proyecto_id),
    INDEX idx_miembros_proyecto_usuario_id (usuario_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
