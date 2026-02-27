import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { DropdownModule } from 'primeng/dropdown';
import { TagModule } from 'primeng/tag';
import { ToolbarModule } from 'primeng/toolbar';
import { TooltipModule } from 'primeng/tooltip';
import { CardModule } from 'primeng/card';
import { CalendarModule } from 'primeng/calendar';
import { MessageService } from 'primeng/api';
import { AuditoriaService } from '../../core/services/auditoria.service';
import { LogAuditoria, EstadisticasAuditoria, FiltrosAuditoria, Paginacion } from '../../core/models';

@Component({
  selector: 'app-auditoria',
  standalone: true,
  imports: [
    CommonModule, FormsModule, TableModule, ButtonModule, InputTextModule,
    DropdownModule, TagModule, ToolbarModule, TooltipModule, CardModule, CalendarModule
  ],
  templateUrl: './auditoria.component.html',
  styleUrls: ['./auditoria.component.scss']
})
export class AuditoriaComponent implements OnInit {
  logs: LogAuditoria[] = [];
  total = 0;
  pagina = 1;
  tamano = 25;
  cargando = false;

  estadisticas: EstadisticasAuditoria | null = null;

  filtros: FiltrosAuditoria = {};

  fechaDesde: Date | null = null;
  fechaHasta: Date | null = null;

  opcionesCategoria = [
    { label: 'Acceso', value: 'acceso' },
    { label: 'Usuario', value: 'usuario' },
    { label: 'Proyecto', value: 'proyecto' },
    { label: 'Tarea', value: 'tarea' },
    { label: 'Etiqueta', value: 'etiqueta' },
    { label: 'Sistema', value: 'sistema' }
  ];

  constructor(
    private auditoriaService: AuditoriaService,
    private messageService: MessageService
  ) {}

  ngOnInit(): void {
    this.cargarEstadisticas();
    this.cargar();
  }

  cargarEstadisticas(): void {
    this.auditoriaService.estadisticas().subscribe({
      next: (stats: EstadisticasAuditoria) => this.estadisticas = stats,
      error: () => this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Error al cargar estadísticas' })
    });
  }

  cargar(): void {
    this.cargando = true;
    const params: FiltrosAuditoria = {
      ...this.filtros,
      pagina: this.pagina,
      tamano_pagina: this.tamano
    };

    if (this.fechaDesde) {
      params.fecha_desde = this.fechaDesde.toISOString();
    }
    if (this.fechaHasta) {
      params.fecha_hasta = this.fechaHasta.toISOString();
    }

    this.auditoriaService.listar(params).subscribe({
      next: (res: Paginacion<LogAuditoria>) => {
        this.logs = res.elementos;
        this.total = res.total;
        this.cargando = false;
      },
      error: () => {
        this.cargando = false;
        this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Error al cargar logs de auditoría' });
      }
    });
  }

  cargarLazy(event: any): void {
    this.pagina = Math.floor((event.first || 0) / (event.rows || this.tamano)) + 1;
    this.tamano = event.rows || this.tamano;
    this.cargar();
  }

  limpiarFiltros(): void {
    this.filtros = {};
    this.fechaDesde = null;
    this.fechaHasta = null;
    this.pagina = 1;
    this.cargar();
  }

  categoriaSeverity(cat: string): 'success' | 'info' | 'warning' | 'danger' | 'secondary' | 'contrast' {
    const map: Record<string, 'success' | 'info' | 'warning' | 'danger' | 'secondary' | 'contrast'> = {
      acceso: 'info',
      usuario: 'warning',
      proyecto: 'success',
      tarea: 'contrast',
      etiqueta: 'secondary',
      sistema: 'danger'
    };
    return map[cat] || 'info';
  }

  categoriaIcon(cat: string): string {
    const map: Record<string, string> = {
      acceso: 'pi pi-sign-in',
      usuario: 'pi pi-user',
      proyecto: 'pi pi-briefcase',
      tarea: 'pi pi-list',
      etiqueta: 'pi pi-tag',
      sistema: 'pi pi-cog'
    };
    return map[cat] || 'pi pi-circle';
  }

  accionLabel(accion: string): string {
    const map: Record<string, string> = {
      login_exitoso: 'Inicio de sesión',
      login_fallido: 'Login fallido',
      login_cuenta_inactiva: 'Cuenta inactiva',
      registro: 'Registro',
      logout: 'Cierre de sesión',
      crear_usuario: 'Crear usuario',
      cambiar_rol: 'Cambiar rol',
      activar_usuario: 'Activar usuario',
      desactivar_usuario: 'Desactivar usuario',
      eliminar_usuario: 'Eliminar usuario',
      reset_password: 'Resetear contraseña',
      crear_proyecto: 'Crear proyecto',
      eliminar_proyecto: 'Eliminar proyecto',
      archivar_proyecto: 'Archivar proyecto',
      restaurar_proyecto: 'Restaurar proyecto',
      crear_tarea: 'Crear tarea',
      eliminar_tarea: 'Eliminar tarea',
      completar_tarea: 'Completar tarea',
      crear_etiqueta: 'Crear etiqueta',
      eliminar_etiqueta: 'Eliminar etiqueta'
    };
    return map[accion] || accion;
  }

  accionSeverity(accion: string): 'success' | 'info' | 'warning' | 'danger' | 'secondary' | 'contrast' {
    if (accion.includes('eliminar') || accion === 'login_fallido' || accion === 'login_cuenta_inactiva') return 'danger';
    if (accion.includes('crear') || accion === 'login_exitoso' || accion === 'registro' || accion === 'activar_usuario') return 'success';
    if (accion.includes('cambiar') || accion.includes('reset') || accion.includes('archivar')) return 'warning';
    if (accion === 'logout' || accion.includes('desactivar')) return 'secondary';
    return 'info';
  }
}
