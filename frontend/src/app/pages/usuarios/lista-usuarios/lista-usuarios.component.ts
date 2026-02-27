import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { DropdownModule } from 'primeng/dropdown';
import { TagModule } from 'primeng/tag';
import { ToolbarModule } from 'primeng/toolbar';
import { TooltipModule } from 'primeng/tooltip';
import { MessageModule } from 'primeng/message';
import { InputSwitchModule } from 'primeng/inputswitch';
import { PasswordModule } from 'primeng/password';
import { ConfirmationService, MessageService } from 'primeng/api';
import { UsuariosService } from '../../../core/services/usuarios.service';
import { AuthService } from '../../../core/services/auth.service';
import { Usuario } from '../../../core/models';

@Component({
  selector: 'app-lista-usuarios',
  standalone: true,
  imports: [
    CommonModule, FormsModule, TableModule, ButtonModule, DialogModule,
    InputTextModule, DropdownModule, TagModule, ToolbarModule, TooltipModule,
    MessageModule, InputSwitchModule, PasswordModule
  ],
  templateUrl: './lista-usuarios.component.html',
  styleUrls: ['./lista-usuarios.component.scss']
})
export class ListaUsuariosComponent implements OnInit {
  usuarios: Usuario[] = [];
  total = 0;
  pagina = 1;
  tamano = 20;
  cargando = false;

  filtros: {
    buscar?: string;
    rol?: string;
    activo?: string;
  } = {};

  opcionesRol = [
    { label: 'Administrador', value: 'administrador' },
    { label: 'Jefe', value: 'jefe' },
    { label: 'Usuario', value: 'usuario' },
    { label: 'Visualizador', value: 'visualizador' }
  ];

  opcionesActivo = [
    { label: 'Activo', value: 'true' },
    { label: 'Inactivo', value: 'false' }
  ];

  // Dialog crear/editar
  dialogoVisible = false;
  usuarioEditar: Usuario | null = null;
  form: any = this.formVacio();
  formError = '';
  guardando = false;

  // Dialog reset password
  dialogoPassword = false;
  usuarioPassword: Usuario | null = null;
  nuevaContrasena = '';
  passwordError = '';
  guardandoPassword = false;

  constructor(
    private usuariosService: UsuariosService,
    private messageService: MessageService,
    private confirmationService: ConfirmationService,
    public authService: AuthService
  ) {}

  get esAdmin(): boolean {
    return this.authService.esAdmin;
  }

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.cargando = true;
    const params: Record<string, any> = {
      pagina: this.pagina,
      tamano_pagina: this.tamano,
      ...this.filtros
    };
    this.usuariosService.listar(params).subscribe({
      next: res => {
        this.usuarios = res.elementos;
        this.total = res.total;
        this.cargando = false;
      },
      error: () => {
        this.cargando = false;
        this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Error al cargar usuarios' });
      }
    });
  }

  cargarLazy(event: any): void {
    this.pagina = Math.floor(event.first / event.rows) + 1;
    this.tamano = event.rows;
    this.cargar();
  }

  abrirDialogo(): void {
    this.usuarioEditar = null;
    this.form = this.formVacio();
    this.formError = '';
    this.dialogoVisible = true;
  }

  editar(usuario: Usuario): void {
    this.usuarioEditar = usuario;
    this.form = {
      nombre_completo: usuario.nombre_completo,
      correo: usuario.correo,
      rol: usuario.rol,
      esta_activo: usuario.esta_activo,
      contrasena: ''
    };
    this.formError = '';
    this.dialogoVisible = true;
  }

  guardar(): void {
    if (!this.form.nombre_completo || !this.form.correo) {
      this.formError = 'Nombre y correo son obligatorios';
      return;
    }
    this.guardando = true;
    if (this.usuarioEditar) {
      const data: any = {
        nombre_completo: this.form.nombre_completo,
        correo: this.form.correo,
        rol: this.form.rol,
        esta_activo: this.form.esta_activo
      };
      this.usuariosService.actualizar(this.usuarioEditar.id, data).subscribe({
        next: () => {
          this.messageService.add({ severity: 'success', summary: 'Éxito', detail: 'Usuario actualizado' });
          this.dialogoVisible = false;
          this.guardando = false;
          this.cargar();
        },
        error: err => {
          this.formError = err.error?.error || 'Error al actualizar';
          this.guardando = false;
        }
      });
    } else {
      if (!this.form.contrasena || this.form.contrasena.length < 8) {
        this.formError = 'La contraseña debe tener al menos 8 caracteres';
        this.guardando = false;
        return;
      }
      this.usuariosService.crear(this.form).subscribe({
        next: () => {
          this.messageService.add({ severity: 'success', summary: 'Éxito', detail: 'Usuario creado' });
          this.dialogoVisible = false;
          this.guardando = false;
          this.cargar();
        },
        error: err => {
          this.formError = err.error?.error || 'Error al crear usuario';
          this.guardando = false;
        }
      });
    }
  }

  eliminar(usuario: Usuario): void {
    this.confirmationService.confirm({
      message: `¿Eliminar al usuario "${usuario.nombre_completo}"? Esta acción eliminará todos sus proyectos, tareas y etiquetas.`,
      header: 'Confirmar eliminación',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Eliminar',
      rejectLabel: 'Cancelar',
      acceptButtonStyleClass: 'p-button-danger',
      accept: () => {
        this.usuariosService.eliminar(usuario.id).subscribe({
          next: () => {
            this.messageService.add({ severity: 'success', summary: 'Éxito', detail: 'Usuario eliminado' });
            this.cargar();
          },
          error: err => {
            this.messageService.add({ severity: 'error', summary: 'Error', detail: err.error?.error || 'Error al eliminar' });
          }
        });
      }
    });
  }

  abrirResetPassword(usuario: Usuario): void {
    this.usuarioPassword = usuario;
    this.nuevaContrasena = '';
    this.passwordError = '';
    this.dialogoPassword = true;
  }

  resetPassword(): void {
    if (!this.nuevaContrasena || this.nuevaContrasena.length < 8) {
      this.passwordError = 'La contraseña debe tener al menos 8 caracteres';
      return;
    }
    this.guardandoPassword = true;
    this.usuariosService.resetPassword(this.usuarioPassword!.id, this.nuevaContrasena).subscribe({
      next: () => {
        this.messageService.add({ severity: 'success', summary: 'Éxito', detail: 'Contraseña restablecida' });
        this.dialogoPassword = false;
        this.guardandoPassword = false;
      },
      error: err => {
        this.passwordError = err.error?.error || 'Error al restablecer';
        this.guardandoPassword = false;
      }
    });
  }

  toggleActivo(usuario: Usuario): void {
    this.usuariosService.actualizar(usuario.id, { esta_activo: !usuario.esta_activo }).subscribe({
      next: () => {
        this.messageService.add({
          severity: 'success', summary: 'Éxito',
          detail: `Usuario ${!usuario.esta_activo ? 'activado' : 'desactivado'}`
        });
        this.cargar();
      },
      error: () => {
        this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Error al cambiar estado' });
      }
    });
  }

  rolLabel(rol: string): string {
    const map: Record<string, string> = {
      'administrador': 'Administrador',
      'jefe': 'Jefe',
      'usuario': 'Usuario',
      'visualizador': 'Visualizador'
    };
    return map[rol] || rol;
  }

  rolSeverity(rol: string): "success" | "secondary" | "info" | "warning" | "danger" | "contrast" | undefined {
    const map: Record<string, "success" | "secondary" | "info" | "warning" | "danger" | "contrast"> = {
      'administrador': 'danger',
      'jefe': 'warning',
      'usuario': 'info',
      'visualizador': 'secondary'
    };
    return map[rol] || 'info';
  }

  rolIcon(rol: string): string {
    const map: Record<string, string> = {
      'administrador': 'pi pi-shield',
      'jefe': 'pi pi-star',
      'usuario': 'pi pi-user',
      'visualizador': 'pi pi-eye'
    };
    return map[rol] || 'pi pi-user';
  }

  private formVacio() {
    return {
      nombre_completo: '',
      correo: '',
      contrasena: '',
      rol: 'usuario',
      esta_activo: true
    };
  }
}
