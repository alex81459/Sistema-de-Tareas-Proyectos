# SQL heredado

Los archivos `agregar_*.sql` se conservan unicamente para llevar instalaciones antiguas al esquema de referencia antes de ejecutar `flask db stamp head`.

Las instalaciones nuevas y los cambios futuros deben usar exclusivamente las migraciones Alembic ubicadas en `backend/migrations`.
