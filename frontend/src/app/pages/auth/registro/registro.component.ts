import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { ButtonModule } from 'primeng/button';
import { DividerModule } from 'primeng/divider';
import { MessageModule } from 'primeng/message';
import { MessageService } from 'primeng/api';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-registro',
  standalone: true,
  imports: [CommonModule, FormsModule, InputTextModule, PasswordModule, ButtonModule, DividerModule, MessageModule, RouterLink],
  templateUrl: './registro.component.html',
  styleUrls: ['./registro.component.scss']
})
export class RegistroComponent {
  nombreCompleto = '';
  correo = '';
  contrasena = '';
  cargando = false;
  error = '';

  constructor(
    private authService: AuthService,
    private router: Router,
    private messageService: MessageService
  ) {}

  registrar(): void {
    if (!this.nombreCompleto || !this.correo || !this.contrasena) {
      this.error = 'Completa todos los campos';
      return;
    }
    if (this.contrasena.length < 8) {
      this.error = 'La contraseña debe tener al menos 8 caracteres';
      return;
    }
    if (!/\d/.test(this.contrasena)) {
      this.error = 'La contraseña debe contener al menos un número';
      return;
    }

    this.cargando = true;
    this.error = '';

    this.authService.registrar({
      correo: this.correo,
      contrasena: this.contrasena,
      nombre_completo: this.nombreCompleto
    }).subscribe({
      next: () => {
        this.messageService.add({ severity: 'success', summary: 'Cuenta creada', detail: 'Bienvenido al sistema' });
        this.router.navigate(['/app/panel']);
      },
      error: (err) => {
        this.cargando = false;
        this.error = err?.error?.error || err?.error?.errores?.contrasena?.[0] || 'Error al registrar';
      }
    });
  }
}
