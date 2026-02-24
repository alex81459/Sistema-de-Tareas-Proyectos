import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import { ResumenPanel } from '../models';

export interface EstadisticasGraficas {
  tareas_por_prioridad: Record<string, number>;
  completadas_por_semana: { semana: string; total: number }[];
  tareas_por_proyecto: { nombre: string; total: number }[];
  creadas_vs_completadas: { semana: string; creadas: number; completadas: number }[];
}

@Injectable({ providedIn: 'root' })
export class PanelService {
  private readonly apiUrl = `${environment.apiUrl}/panel`;

  constructor(private http: HttpClient) {}

  obtenerResumen(fechaDesde?: string, fechaHasta?: string): Observable<ResumenPanel> {
    let params = new HttpParams();
    if (fechaDesde) params = params.set('fecha_desde', fechaDesde);
    if (fechaHasta) params = params.set('fecha_hasta', fechaHasta);
    return this.http.get<ResumenPanel>(`${this.apiUrl}/resumen`, { params });
  }

  obtenerEstadisticasGraficas(): Observable<EstadisticasGraficas> {
    return this.http.get<EstadisticasGraficas>(`${this.apiUrl}/estadisticas-graficas`);
  }
}
