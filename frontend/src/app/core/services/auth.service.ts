import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap, catchError, throwError, BehaviorSubject } from 'rxjs';
import { environment } from '@env/environment';
import { Usuario, LoginRequest, RegistroRequest, AuthResponse } from '../models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly apiUrl = `${environment.apiUrl}/autenticacion`;
  private readonly _usuario = new BehaviorSubject<Usuario | null>(null);

  usuario$ = this._usuario.asObservable();

  constructor(private http: HttpClient, private router: Router) {
    this.cargarUsuarioDesdeStorage();
  }

  get usuario(): Usuario | null {
    return this._usuario.value;
  }

  get estaAutenticado(): boolean {
    return !!this.getAccessToken();
  }

  get esAdmin(): boolean {
    return this.usuario?.rol === 'administrador';
  }

  get esJefe(): boolean {
    return this.usuario?.rol === 'jefe';
  }

  get esVisualizador(): boolean {
    return this.usuario?.rol === 'visualizador';
  }

  get puedeEscribir(): boolean {
    return !!this.usuario && this.usuario.rol !== 'visualizador';
  }

  get puedeVerUsuarios(): boolean {
    return this.esAdmin || this.esJefe;
  }

  get puedeGestionarUsuarios(): boolean {
    return this.esAdmin;
  }

  registrar(data: RegistroRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/registrar`, data).pipe(
      tap(res => this.guardarSesion(res)),
      catchError(this.manejarError)
    );
  }

  iniciarSesion(data: LoginRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/iniciar-sesion`, data).pipe(
      tap(res => {
        this.guardarSesion(res);
      }),
      catchError((error) => {
        return this.manejarError(error);
      })
    );
  }

  cerrarSesion(): void {
    this.http.post(`${this.apiUrl}/cerrar-sesion`, {}).subscribe({ error: () => {} });
    this.limpiarSesion();
    this.router.navigate(['/iniciar-sesion']);
  }

  actualizarToken(): Observable<{ access_token: string; refresh_token: string }> {
    const refreshToken = this.getRefreshToken();
    return this.http.post<{ access_token: string; refresh_token: string }>(
      `${this.apiUrl}/actualizar-token`,
      {},
      { headers: { Authorization: `Bearer ${refreshToken}` } }
    ).pipe(
      tap(res => {
        localStorage.setItem('access_token', res.access_token);
        localStorage.setItem('refresh_token', res.refresh_token);
      })
    );
  }

  obtenerPerfil(): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.apiUrl}/perfil`).pipe(
      tap(u => {
        this._usuario.next(u);
        localStorage.setItem('usuario', JSON.stringify(u));
      })
    );
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  private guardarSesion(res: AuthResponse): void {
    try {
      localStorage.setItem('access_token', res.access_token);
      localStorage.setItem('refresh_token', res.refresh_token);
      localStorage.setItem('usuario', JSON.stringify(res.usuario));
      this._usuario.next(res.usuario);
    } catch (err) {
      throw err;
    }
  }

  private limpiarSesion(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('usuario');
    this._usuario.next(null);
  }

  private cargarUsuarioDesdeStorage(): void {
    const data = localStorage.getItem('usuario');
    if (data) {
      try {
        this._usuario.next(JSON.parse(data));
      } catch { }
    }
  }

  private manejarError(error: any): Observable<never> {
    return throwError(() => error);
  }
}
    