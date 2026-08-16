import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { DividerModule } from 'primeng/divider';
import { ChipModule } from 'primeng/chip';
import { BadgeModule } from 'primeng/badge';
import { TooltipModule } from 'primeng/tooltip';
import { FormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { DropdownModule } from 'primeng/dropdown';
import { MessageModule } from 'primeng/message';
import { MessageService, ConfirmationService } from 'primeng/api';
import { ProyectosService } from '../../../core/services/proyectos.service';
import { TareasService } from '../../../core/services/tareas.service';
import { Proyecto, Tarea, MiembroProyecto, PermisoProyecto } from '../../../core/models';

@Component({
  selector: 'app-detalle-proyecto',
  standalone: true,
  imports: [
    CommonModule, CardModule, ButtonModule, TagModule, DividerModule, ChipModule,
    BadgeModule, TooltipModule, RouterLink, FormsModule, InputTextModule,
    DropdownModule, MessageModule
  ],
  templateUrl: './detalle-proyecto.component.html',
  styleUrls: ['./detalle-proyecto.component.scss']
})
export class DetalleProyectoComponent implements OnInit {
  proyecto: Proyecto | null = null;
  tareas: Tarea[] = [];
  miembros: MiembroProyecto[] = [];
  cargandoMiembros = false;
  guardandoMiembro = false;
  errorMiembro = '';
  formularioMiembro = {
    correo: '',
    permiso: 'lectura' as PermisoProyecto
  };
  opcionesPermiso = [
    { label: 'Lectura', value: 'lectura' as PermisoProyecto },
    { label: 'Edición', value: 'edicion' as PermisoProyecto },
    { label: 'Administración', value: 'administracion' as PermisoProyecto },
  ];
  private proyectoId = 0;

  constructor(
    private route: ActivatedRoute,
    private proyectosService: ProyectosService,
    private tareasService: TareasService,
    private messageService: MessageService,
    private confirmationService: ConfirmationService
  ) {}

  ngOnInit(): void {
    this.proyectoId = Number(this.route.snapshot.paramMap.get('id'));
    this.cargarProyecto();
    this.cargarMiembros();
    this.tareasService.listar({ proyecto_id: this.proyectoId, tamano_pagina: 100 }).subscribe(
      res => this.tareas = res.elementos
    );
  }

  get puedeAdministrar(): boolean {
    return !!this.proyecto?.puede_administrar;
  }

  cargarProyecto(): void {
    this.proyectosService.obtener(this.proyectoId).subscribe(p => this.proyecto = p);
  }

  cargarMiembros(): void {
    this.cargandoMiembros = true;
    this.proyectosService.listarMiembros(this.proyectoId).subscribe({
      next: miembros => {
        this.miembros = miembros;
        this.cargandoMiembros = false;
      },
      error: () => {
        this.cargandoMiembros = false;
      }
    });
  }

  agregarMiembro(): void {
    if (!this.formularioMiembro.correo.trim()) {
      this.errorMiembro = 'Ingresa el correo del usuario';
      return;
    }

    this.guardandoMiembro = true;
    this.errorMiembro = '';
    this.proyectosService.agregarMiembro(this.proyectoId, {
      correo: this.formularioMiembro.correo.trim(),
      permiso: this.formularioMiembro.permiso,
    }).subscribe({
      next: miembro => {
        this.miembros = [...this.miembros, miembro];
        this.formularioMiembro = { correo: '', permiso: 'lectura' };
        this.guardandoMiembro = false;
        this.cargarProyecto();
        this.messageService.add({ severity: 'success', summary: 'Miembro agregado', detail: miembro.correo });
      },
      error: (error) => {
        this.guardandoMiembro = false;
        this.errorMiembro = error?.error?.error || 'No se pudo agregar el miembro';
      }
    });
  }

  cambiarPermiso(miembro: MiembroProyecto, permiso: PermisoProyecto): void {
    if (miembro.permiso === permiso) {
      return;
    }

    const permisoAnterior = miembro.permiso;
    miembro.permiso = permiso;
    this.proyectosService.actualizarMiembro(this.proyectoId, miembro.usuario_id, permiso).subscribe({
      next: (miembroActualizado) => {
        miembro.permiso = miembroActualizado.permiso;
        this.cargarProyecto();
        this.messageService.add({ severity: 'success', summary: 'Permiso actualizado', detail: miembro.correo });
      },
      error: (error) => {
        miembro.permiso = permisoAnterior;
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: error?.error?.error || 'No se pudo actualizar el permiso'
        });
      }
    });
  }

  quitarMiembro(miembro: MiembroProyecto): void {
    this.confirmationService.confirm({
      message: `¿Quitar a ${miembro.correo} de este proyecto?`,
      header: 'Quitar miembro',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Quitar',
      rejectLabel: 'Cancelar',
      accept: () => {
        this.proyectosService.eliminarMiembro(this.proyectoId, miembro.usuario_id).subscribe({
          next: () => {
            this.miembros = this.miembros.filter(item => item.usuario_id !== miembro.usuario_id);
            this.cargarProyecto();
            this.messageService.add({ severity: 'info', summary: 'Miembro eliminado', detail: miembro.correo });
          }
        });
      }
    });
  }
}
