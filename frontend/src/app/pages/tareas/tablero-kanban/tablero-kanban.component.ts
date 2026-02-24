import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  CdkDragDrop,
  CdkDrag,
  CdkDropList,
  DragDropModule,
} from '@angular/cdk/drag-drop';
import { ButtonModule } from 'primeng/button';
import { DropdownModule } from 'primeng/dropdown';
import { TagModule } from 'primeng/tag';
import { ChipModule } from 'primeng/chip';
import { BadgeModule } from 'primeng/badge';
import { ToolbarModule } from 'primeng/toolbar';
import { MessageService } from 'primeng/api';
import { TareasService } from '../../../core/services/tareas.service';
import { ProyectosService } from '../../../core/services/proyectos.service';
import { Tarea, Proyecto } from '../../../core/models';

interface KanbanColumna {
  estado: string;
  titulo: string;
  color: string;
  tareas: Tarea[];
}

@Component({
  selector: 'app-tablero-kanban',
  standalone: true,
  imports: [CommonModule, FormsModule, DragDropModule, ButtonModule, DropdownModule, TagModule, ChipModule, BadgeModule, ToolbarModule],
  templateUrl: './tablero-kanban.component.html',
  styleUrls: ['./tablero-kanban.component.scss']
})
export class TableroKanbanComponent implements OnInit {
  columnas: KanbanColumna[] = [
    { estado: 'pendiente', titulo: 'Pendiente', color: '#64748b', tareas: [] },
    { estado: 'en_progreso', titulo: 'En Progreso', color: '#3b82f6', tareas: [] },
    { estado: 'completada', titulo: 'Completada', color: '#10b981', tareas: [] },
  ];

  filtroProyecto: number | null = null;
  opcionesProyecto: { label: string; value: number }[] = [];

  constructor(
    private tareasService: TareasService,
    private proyectosService: ProyectosService,
    private messageService: MessageService
  ) {}

  ngOnInit(): void {
    this.proyectosService.listar({ tamano_pagina: 100, estado: 'activo' }).subscribe(res => {
      this.opcionesProyecto = res.elementos.map(p => ({ label: p.nombre, value: p.id }));
    });
    this.cargar();
  }

  cargar(): void {
    const params: Record<string, any> = { tamano_pagina: 200 };
    if (this.filtroProyecto) params['proyecto_id'] = this.filtroProyecto;

    this.tareasService.listar(params).subscribe(res => {
      this.columnas.forEach(col => col.tareas = []);
      for (const tarea of res.elementos) {
        const col = this.columnas.find(c => c.estado === tarea.estado);
        if (col) col.tareas.push(tarea);
      }
    });
  }

  getConnectedLists(estado: string): string[] {
    return this.columnas.filter(c => c.estado !== estado).map(c => c.estado);
  }

  drop(event: CdkDragDrop<Tarea[]>, nuevoEstado: string): void {
    if (event.previousContainer === event.container) {
      // Reordenar dentro de la misma columna
      const item = event.container.data.splice(event.previousIndex, 1)[0];
      event.container.data.splice(event.currentIndex, 0, item);
    } else {
      // Mover entre columnas
      const tarea = event.previousContainer.data[event.previousIndex];
      event.previousContainer.data.splice(event.previousIndex, 1);
      event.container.data.splice(event.currentIndex, 0, tarea);

      // Actualizar en backend
      if (nuevoEstado === 'completada') {
        this.tareasService.completar(tarea.id).subscribe({
          next: (t) => {
            Object.assign(tarea, t);
            this.messageService.add({ severity: 'success', summary: 'Completada', detail: tarea.titulo });
          },
          error: () => this.cargar()
        });
      } else if (tarea.estado === 'completada' && nuevoEstado !== 'completada') {
        this.tareasService.reabrir(tarea.id).subscribe({
          next: () => {
            this.tareasService.actualizar(tarea.id, { estado: nuevoEstado }).subscribe({
              next: (t) => Object.assign(tarea, t),
              error: () => this.cargar()
            });
          },
          error: () => this.cargar()
        });
      } else {
        this.tareasService.actualizar(tarea.id, { estado: nuevoEstado }).subscribe({
          next: (t) => Object.assign(tarea, t),
          error: () => this.cargar()
        });
      }
    }
  }
}
