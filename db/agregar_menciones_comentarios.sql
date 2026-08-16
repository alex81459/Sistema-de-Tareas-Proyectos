USE tareas_proyectos;

CREATE TABLE IF NOT EXISTS menciones_comentario (
    id INT NOT NULL AUTO_INCREMENT,
    comentario_id INT NOT NULL,
    usuario_id INT NOT NULL,
    creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_mencion_comentario_usuario UNIQUE (comentario_id, usuario_id),
    CONSTRAINT fk_menciones_comentario_comentario
        FOREIGN KEY (comentario_id) REFERENCES comentarios_tarea (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_menciones_comentario_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        ON DELETE CASCADE,
    INDEX idx_menciones_comentario_comentario_id (comentario_id),
    INDEX idx_menciones_comentario_usuario_id (usuario_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
