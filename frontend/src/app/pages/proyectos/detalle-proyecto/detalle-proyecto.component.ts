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
import { ProyectosService } from '../../../core/services/proyectos.service';
import { TareasService } from '../../../core/services/tareas.service';
import { Proyecto, Tarea } from '../../../core/models';

@Component({
  selector: 'app-detalle-proyecto',
  standalone: true,
  imports: [CommonModule, CardModule, ButtonModule, TagModule, DividerModule, ChipModule, BadgeModule, TooltipModule, RouterLink],
  templateUrl: './detalle-proyecto.component.html',
  styleUrls: ['./detalle-proyecto.component.scss']
})
export class DetalleProyectoComponent implements OnInit {
  proyecto: Proyecto | null = null;
  tareas: Tarea[] = [];

  constructor(
    private route: ActivatedRoute,
    private proyectosService: ProyectosService,
    private tareasService: TareasService
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.proyectosService.obtener(id).subscribe(p => this.proyecto = p);
    this.tareasService.listar({ proyecto_id: id, tamano_pagina: 100 }).subscribe(
      res => this.tareas = res.elementos
    );
  }
}
