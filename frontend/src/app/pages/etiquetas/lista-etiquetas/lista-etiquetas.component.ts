import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { ColorPickerModule } from 'primeng/colorpicker';
import { ToolbarModule } from 'primeng/toolbar';
import { BadgeModule } from 'primeng/badge';
import { AvatarModule } from 'primeng/avatar';
import { CardModule } from 'primeng/card';
import { TooltipModule } from 'primeng/tooltip';
import { MessageModule } from 'primeng/message';
import { ConfirmationService, MessageService } from 'primeng/api';
import { EtiquetasService } from '../../../core/services/etiquetas.service';
import { Etiqueta } from '../../../core/models';

@Component({
  selector: 'app-lista-etiquetas',
  standalone: true,
  imports: [CommonModule, FormsModule, ButtonModule, DialogModule, InputTextModule, ColorPickerModule, ToolbarModule, BadgeModule, AvatarModule, CardModule, TooltipModule, MessageModule],
  templateUrl: './lista-etiquetas.component.html',
  styleUrls: ['./lista-etiquetas.component.scss']
})
export class ListaEtiquetasComponent implements OnInit {
  etiquetas: Etiqueta[] = [];

  dialogoVisible = false;
  etiquetaEditar: Etiqueta | null = null;
  form = { nombre: '', color: '' };
  formColor: string = '3b82f6';
  formError = '';
  guardando = false;

  constructor(
    private etiquetasService: EtiquetasService,
    private messageService: MessageService,
    private confirmationService: ConfirmationService
  ) {}

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.etiquetasService.listar().subscribe(res => this.etiquetas = res);
  }

  abrirDialogo(): void {
    this.etiquetaEditar = null;
    this.form = { nombre: '', color: '' };
    this.formColor = '3b82f6';
    this.formError = '';
    this.dialogoVisible = true;
  }

  editar(e: Etiqueta): void {
    this.etiquetaEditar = e;
    this.form = { nombre: e.nombre, color: e.color || '' };
    this.formColor = (e.color || '#3b82f6').replace('#', '');
    this.formError = '';
    this.dialogoVisible = true;
  }

  guardar(): void {
    if (!this.form.nombre || this.form.nombre.length < 1) {
      this.formError = 'El nombre es requerido';
      return;
    }

    // Sincronizar color del picker
    if (this.formColor && !this.form.color) {
      this.form.color = '#' + this.formColor;
    }

    this.guardando = true;
    const data = { ...this.form };

    const obs = this.etiquetaEditar
      ? this.etiquetasService.actualizar(this.etiquetaEditar.id, data)
      : this.etiquetasService.crear(data);

    obs.subscribe({
      next: () => {
        this.messageService.add({
          severity: 'success',
          summary: this.etiquetaEditar ? 'Actualizada' : 'Creada',
          detail: `Etiqueta ${this.etiquetaEditar ? 'actualizada' : 'creada'} exitosamente`
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

  eliminar(e: Etiqueta): void {
    this.confirmationService.confirm({
      message: `¿Eliminar la etiqueta "${e.nombre}"?`,
      header: 'Confirmar eliminación',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Eliminar',
      rejectLabel: 'Cancelar',
      accept: () => {
        this.etiquetasService.eliminar(e.id).subscribe(() => {
          this.messageService.add({ severity: 'warn', summary: 'Eliminada', detail: 'Etiqueta eliminada' });
          this.cargar();
        });
      }
    });
  }
}
