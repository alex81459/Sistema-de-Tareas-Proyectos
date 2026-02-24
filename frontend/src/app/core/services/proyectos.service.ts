import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import { Proyecto, ProyectoCrear, Paginacion } from '../models';

@Injectable({ providedIn: 'root' })
export class ProyectosService {
  private readonly apiUrl = `${environment.apiUrl}/proyectos`;

  constructor(private http: HttpClient) {}

  listar(params?: {
    estado?: string;
    buscar?: string;
    pagina?: number;
    tamano_pagina?: number;
  }): Observable<Paginacion<Proyecto>> {
    let httpParams = new HttpParams();
    if (params) {
      Object.entries(params).forEach(([key, val]) => {
        if (val !== undefined && val !== null && val !== '') {
          httpParams = httpParams.set(key, String(val));
        }
      });
    }
    return this.http.get<Paginacion<Proyecto>>(this.apiUrl, { params: httpParams });
  }

  obtener(id: number): Observable<Proyecto> {
    return this.http.get<Proyecto>(`${this.apiUrl}/${id}`);
  }

  crear(data: ProyectoCrear): Observable<Proyecto> {
    return this.http.post<Proyecto>(this.apiUrl, data);
  }

  actualizar(id: number, data: Partial<ProyectoCrear>): Observable<Proyecto> {
    return this.http.put<Proyecto>(`${this.apiUrl}/${id}`, data);
  }

  eliminar(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }

  archivar(id: number): Observable<Proyecto> {
    return this.http.post<Proyecto>(`${this.apiUrl}/${id}/archivar`, {});
  }

  restaurar(id: number): Observable<Proyecto> {
    return this.http.post<Proyecto>(`${this.apiUrl}/${id}/restaurar`, {});
  }
}
