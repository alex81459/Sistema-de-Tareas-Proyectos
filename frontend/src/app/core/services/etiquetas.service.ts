import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import { Etiqueta, EtiquetaCrear } from '../models';

@Injectable({ providedIn: 'root' })
export class EtiquetasService {
  private readonly apiUrl = `${environment.apiUrl}/etiquetas`;

  constructor(private http: HttpClient) {}

  listar(): Observable<Etiqueta[]> {
    return this.http.get<Etiqueta[]>(this.apiUrl);
  }

  crear(data: EtiquetaCrear): Observable<Etiqueta> {
    return this.http.post<Etiqueta>(this.apiUrl, data);
  }

  actualizar(id: number, data: Partial<EtiquetaCrear>): Observable<Etiqueta> {
    return this.http.put<Etiqueta>(`${this.apiUrl}/${id}`, data);
  }

  eliminar(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }
}
