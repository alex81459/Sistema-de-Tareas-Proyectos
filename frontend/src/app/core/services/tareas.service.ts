import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import { Tarea, TareaCrear, Paginacion, Comentario, ChecklistItem } from '../models';

@Injectable({ providedIn: 'root' })
export class TareasService {
  private readonly apiUrl = `${environment.apiUrl}/tareas`;

  constructor(private http: HttpClient) {}

  listar(params?: Record<string, any>): Observable<Paginacion<Tarea>> {
    let httpParams = new HttpParams();
    if (params) {
      Object.entries(params).forEach(([key, val]) => {
        if (val !== undefined && val !== null && val !== '') {
          httpParams = httpParams.set(key, String(val));
        }
      });
    }
    return this.http.get<Paginacion<Tarea>>(this.apiUrl, { params: httpParams });
  }

  obtener(id: number): Observable<Tarea> {
    return this.http.get<Tarea>(`${this.apiUrl}/${id}`);
  }

  crear(data: TareaCrear): Observable<Tarea> {
    return this.http.post<Tarea>(this.apiUrl, data);
  }

  actualizar(id: number, data: Partial<TareaCrear & { estado: string }>): Observable<Tarea> {
    return this.http.put<Tarea>(`${this.apiUrl}/${id}`, data);
  }

  eliminar(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }

  completar(id: number): Observable<Tarea> {
    return this.http.post<Tarea>(`${this.apiUrl}/${id}/completar`, {});
  }

  reabrir(id: number): Observable<Tarea> {
    return this.http.post<Tarea>(`${this.apiUrl}/${id}/reabrir`, {});
  }

  recordatorios(dias: number = 1): Observable<Tarea[]> {
    return this.http.get<Tarea[]>(`${this.apiUrl}/recordatorios`, {
      params: { dias: String(dias) }
    });
  }

  exportarExcel(): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/exportar.xlsx`, { responseType: 'blob' });
  }

  listarComentarios(tareaId: number): Observable<Comentario[]> {
    return this.http.get<Comentario[]>(`${this.apiUrl}/${tareaId}/comentarios`);
  }

  crearComentario(tareaId: number, contenido: string): Observable<Comentario> {
    return this.http.post<Comentario>(`${this.apiUrl}/${tareaId}/comentarios`, { contenido });
  }

  listarChecklist(tareaId: number): Observable<ChecklistItem[]> {
    return this.http.get<ChecklistItem[]>(`${this.apiUrl}/${tareaId}/checklist`);
  }

  crearChecklistItem(tareaId: number, descripcion: string): Observable<ChecklistItem> {
    return this.http.post<ChecklistItem>(`${this.apiUrl}/${tareaId}/checklist`, { descripcion });
  }

  actualizarChecklistItem(tareaId: number, itemId: number, data: Partial<ChecklistItem>): Observable<ChecklistItem> {
    return this.http.put<ChecklistItem>(`${this.apiUrl}/${tareaId}/checklist/${itemId}`, data);
  }

  eliminarChecklistItem(tareaId: number, itemId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${tareaId}/checklist/${itemId}`);
  }
}
