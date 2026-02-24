import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { InputTextareaModule } from 'primeng/inputtextarea';
import { DropdownModule } from 'primeng/dropdown';
import { TagModule } from 'primeng/tag';
import { ToolbarModule } from 'primeng/toolbar';
import { MessageModule } from 'primeng/message';
import { TooltipModule } from 'primeng/tooltip';
import { ConfirmationService, MessageService } from 'primeng/api';
import { ProyectosService } from '../../../core/services/proyectos.service';
import { Proyecto } from '../../../core/models';

@Component({
  selector: 'app-lista-proyectos',
  standalone: true,
  imports: [
    CommonModule, FormsModule, TableModule, ButtonModule, DialogModule,
    InputTextModule, InputTextareaModule, DropdownModule, TagModule, ToolbarModule,
    MessageModule, TooltipModule, RouterLink
  ],
  templateUrl: './lista-proyectos.component.html',
  styleUrls: ['./lista-proyectos.component.scss']
})
export class ListaProyectosComponent implements OnInit {
  proyectos: Proyecto[] = [];
  total = 0;
  pagina = 1;
  tamano = 20;
  cargando = false;
  buscar = '';
  filtroEstado: string | null = null;

  dialogoVisible = false;
  proyectoEditar: Proyecto | null = null;
  form = { nombre: '', descripcion: '' };
  formError = '';
  guardando = false;

  opcionesEstado = [
    { label: 'Activo', value: 'activo' },
    { label: 'Archivado', value: 'archivado' }
  ];

  constructor(
    private proyectosService: ProyectosService,
    private messageService: MessageService,
    private confirmationService: ConfirmationService
  ) {}

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.cargando = true;
    this.proyectosService.listar({
      buscar: this.buscar,
      estado: this.filtroEstado || undefined,
      pagina: this.pagina,
      tamano_pagina: this.tamano
    }).subscribe({
      next: (res) => {
        this.proyectos = res.elementos;
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

  abrirDialogo(): void {
    this.proyectoEditar = null;
    this.form = { nombre: '', descripcion: '' };
    this.formError = '';
    this.dialogoVisible = true;
  }

  editar(p: Proyecto): void {
    this.proyectoEditar = p;
    this.form = { nombre: p.nombre, descripcion: p.descripcion || '' };
    this.formError = '';
    this.dialogoVisible = true;
  }

  guardar(): void {
    if (!this.form.nombre || this.form.nombre.length < 3) {
      this.formError = 'El nombre debe tener al menos 3 caracteres';
      return;
    }
    this.guardando = true;

    const obs = this.proyectoEditar
      ? this.proyectosService.actualizar(this.proyectoEditar.id, this.form)
      : this.proyectosService.crear(this.form);

    obs.subscribe({
      next: () => {
        this.messageService.add({
          severity: 'success',
          summary: this.proyectoEditar ? 'Actualizado' : 'Creado',
          detail: `Proyecto ${this.proyectoEditar ? 'actualizado' : 'creado'} exitosamente`
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

  archivar(p: Proyecto): void {
    this.proyectosService.archivar(p.id).subscribe(() => {
      this.messageService.add({ severity: 'info', summary: 'Archivado', detail: 'Proyecto archivado' });
      this.cargar();
    });
  }

  restaurar(p: Proyecto): void {
    this.proyectosService.restaurar(p.id).subscribe(() => {
      this.messageService.add({ severity: 'success', summary: 'Restaurado', detail: 'Proyecto restaurado' });
      this.cargar();
    });
  }

  eliminar(p: Proyecto): void {
    this.confirmationService.confirm({
      message: `¿Eliminar el proyecto "${p.nombre}" y todas sus tareas?`,
      header: 'Confirmar eliminación',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Eliminar',
      rejectLabel: 'Cancelar',
      accept: () => {
        this.proyectosService.eliminar(p.id).subscribe(() => {
          this.messageService.add({ severity: 'warn', summary: 'Eliminado', detail: 'Proyecto eliminado' });
          this.cargar();
        });
      }
    });
  }
}
