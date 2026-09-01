USE tareas_proyectos;

ALTER TABLE usuarios
    ADD COLUMN intentos_login_fallidos INT NOT NULL DEFAULT 0,
    ADD COLUMN bloqueado_hasta DATETIME NULL;

