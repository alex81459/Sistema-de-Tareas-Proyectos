import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import { LogAuditoria, EstadisticasAuditoria, Paginacion, FiltrosAuditoria } from '../models';

@Injectable({ providedIn: 'root' })
export class AuditoriaService {
  private readonly apiUrl = `${environment.apiUrl}/auditoria`;

  constructor(private http: HttpClient) {}

  listar(filtros: FiltrosAuditoria = {}): Observable<Paginacion<LogAuditoria>> {
    let params = new HttpParams();
    for (const key of Object.keys(filtros) as Array<keyof FiltrosAuditoria>) {
      const val = filtros[key];
      if (val !== null && val !== undefined && val !== '') {
        params = params.set(key, String(val));
      }
    }
    return this.http.get<Paginacion<LogAuditoria>>(this.apiUrl, { params });
  }

  estadisticas(): Observable<EstadisticasAuditoria> {
    return this.http.get<EstadisticasAuditoria>(`${this.apiUrl}/estadisticas`);
  }
}
