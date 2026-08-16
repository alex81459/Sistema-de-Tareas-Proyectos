import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { InputTextareaModule } from 'primeng/inputtextarea';
import { DropdownModule } from 'primeng/dropdown';
import { MultiSelectModule } from 'primeng/multiselect';
import { CalendarModule } from 'primeng/calendar';
import { TagModule } from 'primeng/tag';
import { TooltipModule } from 'primeng/tooltip';
import { ToolbarModule } from 'primeng/toolbar';
import { ChipModule } from 'primeng/chip';
import { MessageModule } from 'primeng/message';
import { AvatarModule } from 'primeng/avatar';
import { ConfirmationService, MessageService } from 'primeng/api';
import { TareasService } from '../../../core/services/tareas.service';
import { ProyectosService } from '../../../core/services/proyectos.service';
import { EtiquetasService } from '../../../core/services/etiquetas.service';
import { Tarea, Proyecto, Etiqueta, Comentario, UsuarioResumen } from '../../../core/models';

@Component({
  selector: 'app-lista-tareas',
  standalone: true,
  imports: [
    CommonModule, FormsModule, TableModule, ButtonModule, DialogModule,
    InputTextModule, InputTextareaModule, DropdownModule, MultiSelectModule,
    CalendarModule, TagModule, TooltipModule, ToolbarModule, ChipModule, MessageModule,
    AvatarModule
  ],
  templateUrl: './lista-tareas.component.html',
  styleUrls: ['./lista-tareas.component.scss']
})
export class ListaTareasComponent implements OnInit {
  tareas: Tarea[] = [];
  total = 0;
  pagina = 1;
  tamano = 20;
  cargando = false;

  filtros: {
    buscar?: string;
    proyecto_id?: number;
    estado?: string;
    prioridad?: string;
    vencida?: string;
    asignado_a_usuario_id?: number;
  } = {};

  proyectos: Proyecto[] = [];
  etiquetas: Etiqueta[] = [];
  opcionesProyecto: { label: string; value: number }[] = [];
  opcionesEtiqueta: { label: string; value: number }[] = [];
  opcionesAsignadoFiltro: { label: string; value: number }[] = [];
  opcionesAsignadoA: { label: string; value: number }[] = [];

  opcionesEstado = [
    { label: 'Pendiente', value: 'pendiente' },
    { label: 'En Progreso', value: 'en_progreso' },
    { label: 'Completada', value: 'completada' }
  ];
  opcionesPrioridad = [
    { label: 'Baja', value: 'baja' },
    { label: 'Media', value: 'media' },
    { label: 'Alta', value: 'alta' },
    { label: 'Urgente', value: 'urgente' }
  ];

  dialogoVisible = false;
  tareaEditar: Tarea | null = null;
  form: any = this.formVacio();
  formFechaVencimiento: Date | null = null;
  formError = '';
  guardando = false;

  constructor(
    private tareasService: TareasService,
    private proyectosService: ProyectosService,
    private etiquetasService: EtiquetasService,
    private messageService: MessageService,
    private confirmationService: ConfirmationService
  ) {}

  ngOnInit(): void {
    this.cargarCatalogos();
    this.cargar();
  }

  cargarCatalogos(): void {
    this.proyectosService.listar({ tamano_pagina: 100, estado: 'activo' }).subscribe(res => {
      this.proyectos = res.elementos;
      this.opcionesProyecto = res.elementos.map(p => ({ label: p.nombre, value: p.id }));
      this.actualizarOpcionesAsignadoFiltro();
      this.actualizarOpcionesAsignadoA(this.form.proyecto_id || undefined);
    });
    this.etiquetasService.listar().subscribe(res => {
      this.etiquetas = res;
      this.opcionesEtiqueta = res.map(e => ({ label: e.nombre, value: e.id }));
    });
  }

  cargar(): void {
    this.cargando = true;
    const params: Record<string, any> = {
      ...this.filtros,
      pagina: this.pagina,
      tamano_pagina: this.tamano
    };
    this.tareasService.listar(params).subscribe({
      next: (res) => {
        this.tareas = res.elementos;
        this.total = res.total;
        this.cargando = false;
      },
      error: () => this.cargando = false
    });
  }

  cargarLazy(event: any): void {
    this.pagina = (event.first / event.rows) + 1;
    this.tamano = event.rows;
    this.cargar();
  }

  formVacio(): any {
    return {
      proyecto_id: null,
      titulo: '',
      descripcion: '',
      estado: 'pendiente',
      prioridad: 'media',
      asignado_a_usuario_id: null,
      etiquetas_ids: []
    };
  }

  abrirDialogo(): void {
    this.tareaEditar = null;
    this.form = this.formVacio();
    this.actualizarOpcionesAsignadoA();
    this.formFechaVencimiento = null;
    this.formError = '';
    this.dialogoVisible = true;
  }

  editar(t: Tarea): void {
    this.tareaEditar = t;
    this.form = {
      proyecto_id: t.proyecto_id,
      titulo: t.titulo,
      descripcion: t.descripcion || '',
      estado: t.estado,
      prioridad: t.prioridad,
      asignado_a_usuario_id: t.asignado_a?.id ?? null,
      etiquetas_ids: t.etiquetas.map(e => e.id)
    };
    this.actualizarOpcionesAsignadoA(t.proyecto_id);
    this.formFechaVencimiento = t.fecha_vencimiento ? new Date(t.fecha_vencimiento + 'T00:00:00') : null;
    this.formError = '';
    this.dialogoVisible = true;
  }

  alCambiarProyecto(): void {
    this.actualizarOpcionesAsignadoA(this.form.proyecto_id || undefined);
    if (
      this.form.asignado_a_usuario_id &&
      !this.opcionesAsignadoA.some(opcion => opcion.value === this.form.asignado_a_usuario_id)
    ) {
      this.form.asignado_a_usuario_id = null;
    }
  }

  actualizarOpcionesAsignadoA(proyectoId?: number): void {
    if (!proyectoId) {
      this.opcionesAsignadoA = [];
      return;
    }

    const proyecto = this.proyectos.find(item => item.id === proyectoId);
    if (!proyecto) {
      this.opcionesAsignadoA = [];
      return;
    }

    const participantes = new Map<number, UsuarioResumen>();

    if (proyecto.propietario) {
      participantes.set(proyecto.propietario.id, proyecto.propietario);
    }

    for (const miembro of (proyecto.miembros || [])) {
      participantes.set(miembro.usuario_id, {
        id: miembro.usuario_id,
        correo: miembro.correo,
        nombre_completo: miembro.nombre_completo,
      });
    }

    this.opcionesAsignadoA = Array.from(participantes.values())
      .map(usuario => ({
        label: `${usuario.nombre_completo} (${usuario.correo})`,
        value: usuario.id,
      }))
      .sort((a, b) => a.label.localeCompare(b.label));
  }

  actualizarOpcionesAsignadoFiltro(): void {
    const participantes = new Map<number, UsuarioResumen>();

    for (const proyecto of this.proyectos) {
      if (proyecto.propietario) {
        participantes.set(proyecto.propietario.id, proyecto.propietario);
      }

      for (const miembro of (proyecto.miembros || [])) {
        participantes.set(miembro.usuario_id, {
          id: miembro.usuario_id,
          correo: miembro.correo,
          nombre_completo: miembro.nombre_completo,
        });
      }
    }

    this.opcionesAsignadoFiltro = Array.from(participantes.values())
      .map(usuario => ({
        label: `${usuario.nombre_completo} (${usuario.correo})`,
        value: usuario.id,
      }))
      .sort((a, b) => a.label.localeCompare(b.label));
  }

  guardar(): void {
    if (!this.form.proyecto_id) { this.formError = 'Selecciona un proyecto'; return; }
    if (!this.form.titulo || this.form.titulo.length < 3) { this.formError = 'El título debe tener al menos 3 caracteres'; return; }

    this.guardando = true;
    const data: any = { ...this.form };
    if (this.formFechaVencimiento) {
      const d = this.formFechaVencimiento;
      data.fecha_vencimiento = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    } else {
      data.fecha_vencimiento = null;
    }

    const obs = this.tareaEditar
      ? this.tareasService.actualizar(this.tareaEditar.id, data)
      : this.tareasService.crear(data);

    obs.subscribe({
      next: () => {
        this.messageService.add({
          severity: 'success',
          summary: this.tareaEditar ? 'Actualizada' : 'Creada',
          detail: `Tarea ${this.tareaEditar ? 'actualizada' : 'creada'} exitosamente`
        });
        this.dialogoVisible = false;
        this.guardando = false;
        this.cargar();
      },
      error: (err) => {
        this.guardando = false;
        this.formError = err?.error?.error || 'Error al guardar';
      }
    });
  }

  completar(t: Tarea): void {
    this.tareasService.completar(t.id).subscribe(() => {
      this.messageService.add({ severity: 'success', summary: 'Completada', detail: 'Tarea marcada como completada' });
      this.cargar();
    });
  }

  reabrir(t: Tarea): void {
    this.tareasService.reabrir(t.id).subscribe(() => {
      this.messageService.add({ severity: 'info', summary: 'Reabierta', detail: 'Tarea reabierta' });
      this.cargar();
    });
  }

  eliminar(t: Tarea): void {
    this.confirmationService.confirm({
      message: `¿Eliminar la tarea "${t.titulo}"?`,
      header: 'Confirmar eliminación',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Eliminar',
      rejectLabel: 'Cancelar',
      accept: () => {
        this.tareasService.eliminar(t.id).subscribe(() => {
          this.messageService.add({ severity: 'warn', summary: 'Eliminada', detail: 'Tarea eliminada' });
          this.cargar();
        });
      }
    });
  }

  exportar(): void {
    this.tareasService.exportarExcel().subscribe(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'tareas.xlsx';
      a.click();
      window.URL.revokeObjectURL(url);
    });
  }

  obtenerTextoAsignado(tarea: Tarea): string {
    return tarea.asignado_a?.nombre_completo || 'Sin asignar';
  }

  // ── Comentarios ──
  dialogoComentarios = false;
  tareaComentarios: Tarea | null = null;
  comentarios: Comentario[] = [];
  nuevoComentario = '';
  enviandoComentario = false;
  cargandoComentarios = false;
  sugerenciasMencion: { etiqueta: string; insercion: string }[] = [];

  abrirComentarios(t: Tarea): void {
    this.tareaComentarios = t;
    this.nuevoComentario = '';
    this.sugerenciasMencion = this.obtenerSugerenciasMencion(t.proyecto_id);
    this.cargandoComentarios = true;
    this.dialogoComentarios = true;
    this.tareasService.listarComentarios(t.id).subscribe({
      next: res => {
        this.comentarios = res;
        this.cargandoComentarios = false;
      },
      error: () => this.cargandoComentarios = false
    });
  }

  enviarComentario(): void {
    if (!this.nuevoComentario.trim() || !this.tareaComentarios) return;
    this.enviandoComentario = true;
    this.tareasService.crearComentario(this.tareaComentarios.id, this.nuevoComentario.trim()).subscribe({
      next: c => {
        this.comentarios.unshift(c);
        this.nuevoComentario = '';
        this.enviandoComentario = false;
        this.messageService.add({ severity: 'success', summary: 'Comentario', detail: 'Comentario agregado' });
      },
      error: () => {
        this.enviandoComentario = false;
        this.messageService.add({ severity: 'error', summary: 'Error', detail: 'No se pudo agregar el comentario' });
      }
    });
  }

  obtenerSugerenciasMencion(proyectoId: number): { etiqueta: string; insercion: string }[] {
    const proyecto = this.proyectos.find(item => item.id === proyectoId);
    if (!proyecto) {
      return [];
    }

    const participantes = new Map<number, UsuarioResumen>();

    if (proyecto.propietario) {
      participantes.set(proyecto.propietario.id, proyecto.propietario);
    }

    for (const miembro of (proyecto.miembros || [])) {
      participantes.set(miembro.usuario_id, {
        id: miembro.usuario_id,
        correo: miembro.correo,
        nombre_completo: miembro.nombre_completo,
      });
    }

    return Array.from(participantes.values())
      .map(usuario => ({
        etiqueta: `${usuario.nombre_completo} (${usuario.correo})`,
        insercion: `@[${usuario.correo}]`,
      }))
      .sort((a, b) => a.etiqueta.localeCompare(b.etiqueta));
  }

  insertarMencion(insercion: string): void {
    this.nuevoComentario = this.nuevoComentario
      ? `${this.nuevoComentario.trimEnd()} ${insercion} `
      : `${insercion} `;
  }
}
