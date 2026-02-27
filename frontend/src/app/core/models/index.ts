export type Rol = 'administrador' | 'jefe' | 'usuario' | 'visualizador';

export interface Usuario {
  id: number;
  correo: string;
  nombre_completo: string;
  rol: Rol;
  esta_activo: boolean;
  creado_en: string;
  actualizado_en: string;
}

export interface LoginRequest {
  correo: string;
  contrasena: string;
  recordarSesion?: boolean;
}

export interface RegistroRequest {
  correo: string;
  contrasena: string;
  nombre_completo: string;
}

export interface AuthResponse {
  usuario: Usuario;
  access_token: string;
  refresh_token: string;
  mensaje?: string;
}

export interface Proyecto {
  id: number;
  usuario_id: number;
  nombre: string;
  descripcion: string | null;
  estado: 'activo' | 'archivado';
  creado_en: string;
  actualizado_en: string;
}

export interface ProyectoCrear {
  nombre: string;
  descripcion?: string;
}

export interface Tarea {
  id: number;
  proyecto_id: number;
  titulo: string;
  descripcion: string | null;
  estado: 'pendiente' | 'en_progreso' | 'completada';
  prioridad: 'baja' | 'media' | 'alta' | 'urgente';
  fecha_vencimiento: string | null;
  completado_en: string | null;
  esta_vencida: boolean;
  nombre_proyecto: string | null;
  etiquetas: Etiqueta[];
  creado_en: string;
  actualizado_en: string;
}

export interface TareaCrear {
  proyecto_id: number;
  titulo: string;
  descripcion?: string;
  estado?: string;
  prioridad?: string;
  fecha_vencimiento?: string | null;
  etiquetas_ids?: number[];
}

export interface Etiqueta {
  id: number;
  usuario_id: number;
  nombre: string;
  color: string | null;
  creado_en: string;
}

export interface EtiquetaCrear {
  nombre: string;
  color?: string;
}

export interface Paginacion<T> {
  elementos: T[];
  pagina: number;
  tamano_pagina: number;
  total: number;
  paginas: number;
}

export interface ResumenPanel {
  conteo_por_estado: Record<string, number>;
  tareas_vencidas: number;
  proximas_a_vencer: number;
  etiquetas_mas_usadas: { id: number; nombre: string; color: string; total: number }[];
  tareas_completadas_rango: number;
  total_proyectos_activos: number;
}

export interface Comentario {
  id: number;
  tarea_id: number;
  usuario_id: number;
  contenido: string;
  creado_en: string;
}

export interface ChecklistItem {
  id: number;
  tarea_id: number;
  descripcion: string;
  esta_completado: boolean;
  creado_en: string;
}

export interface UsuarioCrear {
  correo: string;
  contrasena: string;
  nombre_completo: string;
  rol?: Rol;
}

export interface UsuarioActualizar {
  nombre_completo?: string;
  correo?: string;
  rol?: Rol;
  esta_activo?: boolean;
}

//auditoría de seguridad
export type CategoriaAuditoria = 'acceso' | 'usuario' | 'proyecto' | 'tarea' | 'etiqueta' | 'sistema';

export interface LogAuditoria {
  id: number;
  usuario_id: number | null;
  usuario_correo: string;
  categoria: CategoriaAuditoria;
  accion: string;
  detalle: string | null;
  entidad_tipo: string | null;
  entidad_id: number | null;
  direccion_ip: string | null;
  agente_usuario: string | null;
  creado_en: string;
}

export interface EstadisticasAuditoria {
  total: number;
  eventos_24h: number;
  eventos_7d: number;
  logins_fallidos_24h: number;
  por_categoria: Record<string, number>;
}

export interface FiltrosAuditoria {
  categoria?: string;
  accion?: string;
  usuario_correo?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
  direccion_ip?: string;
  pagina?: number;
  tamano_pagina?: number;
}
