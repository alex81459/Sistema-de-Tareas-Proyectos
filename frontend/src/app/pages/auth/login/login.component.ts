import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { ButtonModule } from 'primeng/button';
import { DividerModule } from 'primeng/divider';
import { MessageModule } from 'primeng/message';
import { CheckboxModule } from 'primeng/checkbox';
import { MessageService } from 'primeng/api';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, InputTextModule, PasswordModule, ButtonModule, DividerModule, MessageModule, CheckboxModule, RouterLink],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  correo = '';
  contrasena = '';
  recordarSesion = false;
  cargando = false;
  error = '';

  constructor(
    private authService: AuthService,
    private router: Router,
    private messageService: MessageService
  ) {}

  iniciarSesion(): void {
    if (!this.correo || !this.contrasena) {
      this.error = 'Completa todos los campos';
      return;
    }
    this.cargando = true;
    this.error = '';

    this.authService.iniciarSesion({
      correo: this.correo,
      contrasena: this.contrasena,
      recordarSesion: this.recordarSesion
    }).subscribe({
      next: (response) => {
        this.messageService.add({ severity: 'success', summary: 'Bienvenido', detail: 'Sesión iniciada correctamente' });
        this.router.navigate(['/app/panel']);
      },
      error: (err) => {
        this.cargando = false;
        let mensaje = 'Error al iniciar sesión';
        
        if (err?.error?.error) {
          mensaje = err.error.error;
        } else if (err?.error?.errores) {
          mensaje = Object.values(err.error.errores).join(', ');
        } else if (err?.message) {
          mensaje = err.message;
        }
        
        this.error = mensaje;
      }
    });
  }
}
