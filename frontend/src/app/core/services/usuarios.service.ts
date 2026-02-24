import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import { Usuario, UsuarioCrear, UsuarioActualizar, Paginacion } from '../models';

@Injectable({ providedIn: 'root' })
export class UsuariosService {
  private readonly apiUrl = `${environment.apiUrl}/usuarios`;

  constructor(private http: HttpClient) {}

  listar(filtros: Record<string, any> = {}): Observable<Paginacion<Usuario>> {
    let params = new HttpParams();
    for (const key of Object.keys(filtros)) {
      if (filtros[key] !== null && filtros[key] !== undefined && filtros[key] !== '') {
        params = params.set(key, filtros[key]);
      }
    }
    return this.http.get<Paginacion<Usuario>>(this.apiUrl, { params });
  }

  obtener(id: number): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.apiUrl}/${id}`);
  }

  crear(data: UsuarioCrear): Observable<{ mensaje: string; usuario: Usuario }> {
    return this.http.post<{ mensaje: string; usuario: Usuario }>(this.apiUrl, data);
  }

  actualizar(id: number, data: UsuarioActualizar): Observable<{ mensaje: string; usuario: Usuario }> {
    return this.http.put<{ mensaje: string; usuario: Usuario }>(`${this.apiUrl}/${id}`, data);
  }

  eliminar(id: number): Observable<{ mensaje: string }> {
    return this.http.delete<{ mensaje: string }>(`${this.apiUrl}/${id}`);
  }

  resetPassword(id: number, contrasena: string): Observable<{ mensaje: string }> {
    return this.http.put<{ mensaje: string }>(`${this.apiUrl}/${id}/reset-password`, { contrasena });
  }
}
