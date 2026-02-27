import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { DividerModule } from 'primeng/divider';
import { AvatarModule } from 'primeng/avatar';
import { ChipModule } from 'primeng/chip';
import { BadgeModule } from 'primeng/badge';
import { ProgressBarModule } from 'primeng/progressbar';
import { ChartModule } from 'primeng/chart';
import { PanelService, EstadisticasGraficas } from '../../core/services/panel.service';
import { TareasService } from '../../core/services/tareas.service';
import { ThemeService } from '../../core/services/theme.service';
import { ResumenPanel, Tarea } from '../../core/models';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-panel',
  standalone: true,
  imports: [CommonModule, CardModule, ButtonModule, TagModule, DividerModule, AvatarModule, ChipModule, BadgeModule, ProgressBarModule, ChartModule],
  templateUrl: './panel.component.html',
  styleUrls: ['./panel.component.scss']
})
export class PanelComponent implements OnInit, OnDestroy {
  resumen: ResumenPanel | null = null;
  recordatorios: Tarea[] = [];
  progresoGeneral = 0;
  chartPrioridad: any;
  chartPrioridadOpts: any;
  chartSemanal: any;
  chartSemanalOpts: any;
  chartProyectos: any;
  chartProyectosOpts: any;
  chartCreadosVsCompletados: any;
  chartCreadosVsCompletadosOpts: any;

  private estadisticas: EstadisticasGraficas | null = null;
  private themeSub?: Subscription;

  constructor(
    private panelService: PanelService,
    private tareasService: TareasService,
    private themeService: ThemeService
  ) {}

  ngOnInit(): void {
    this.panelService.obtenerResumen().subscribe(res => {
      this.resumen = res;
      const completadas = res.conteo_por_estado['completada'] || 0;
      const total = (res.conteo_por_estado['pendiente'] || 0)
                  + (res.conteo_por_estado['en_progreso'] || 0)
                  + completadas;
      this.progresoGeneral = total > 0 ? Math.round((completadas / total) * 100) : 0;
    });
    this.tareasService.recordatorios(7).subscribe(res => this.recordatorios = res);
    this.panelService.obtenerEstadisticasGraficas().subscribe(stats => {
      this.estadisticas = stats;
      this.construirGraficas(stats);
    });

    this.themeSub = this.themeService.darkMode$.subscribe(() => {
      if (this.estadisticas) {
        this.construirGraficas(this.estadisticas);
      }
    });
  }

  ngOnDestroy(): void {
    this.themeSub?.unsubscribe();
  }

  private construirGraficas(stats: EstadisticasGraficas): void {
    const dark = this.themeService.isDark;
    const textColor = dark ? '#94a3b8' : '#64748b';
    const gridColor = dark ? '#334155' : '#e2e8f0';

    //tareas por prioridad
    this.chartPrioridad = {
      labels: ['Baja', 'Media', 'Alta', 'Urgente'],
      datasets: [{
        data: [
          stats.tareas_por_prioridad['baja'] || 0,
          stats.tareas_por_prioridad['media'] || 0,
          stats.tareas_por_prioridad['alta'] || 0,
          stats.tareas_por_prioridad['urgente'] || 0,
        ],
        backgroundColor: ['#3b82f6', '#f59e0b', '#f97316', '#ef4444'],
        borderWidth: 0,
        hoverOffset: 6,
      }]
    };
    this.chartPrioridadOpts = {
      cutout: '65%',
      plugins: {
        legend: { position: 'bottom', labels: { color: textColor, padding: 16, usePointStyle: true } }
      },
      responsive: true,
      maintainAspectRatio: false,
    };

    // Bar — completadas por semana
    this.chartSemanal = {
      labels: stats.completadas_por_semana.map(s => s.semana),
      datasets: [{
        label: 'Completadas',
        data: stats.completadas_por_semana.map(s => s.total),
        backgroundColor: '#10b981',
        borderRadius: 6,
        maxBarThickness: 40,
      }]
    };
    this.chartSemanalOpts = {
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: textColor }, grid: { display: false } },
        y: { beginAtZero: true, ticks: { color: textColor, stepSize: 1 }, grid: { color: gridColor } }
      },
      responsive: true,
      maintainAspectRatio: false,
    };

    // Horizontal bar — tareas por proyecto
    this.chartProyectos = {
      labels: stats.tareas_por_proyecto.map(p => p.nombre),
      datasets: [{
        label: 'Tareas',
        data: stats.tareas_por_proyecto.map(p => p.total),
        backgroundColor: ['#6366f1', '#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'],
        borderRadius: 6,
        maxBarThickness: 28,
      }]
    };
    this.chartProyectosOpts = {
      indexAxis: 'y' as const,
      plugins: { legend: { display: false } },
      scales: {
        x: { beginAtZero: true, ticks: { color: textColor, stepSize: 1 }, grid: { color: gridColor } },
        y: { ticks: { color: textColor }, grid: { display: false } }
      },
      responsive: true,
      maintainAspectRatio: false,
    };

    // Line — creadas vs completadas
    this.chartCreadosVsCompletados = {
      labels: stats.creadas_vs_completadas.map(s => s.semana),
      datasets: [
        {
          label: 'Creadas',
          data: stats.creadas_vs_completadas.map(s => s.creadas),
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59,130,246,0.1)',
          fill: true,
          tension: 0.3,
          pointRadius: 4,
          pointHoverRadius: 6,
        },
        {
          label: 'Completadas',
          data: stats.creadas_vs_completadas.map(s => s.completadas),
          borderColor: '#10b981',
          backgroundColor: 'rgba(16,185,129,0.1)',
          fill: true,
          tension: 0.3,
          pointRadius: 4,
          pointHoverRadius: 6,
        }
      ]
    };
    this.chartCreadosVsCompletadosOpts = {
      plugins: { legend: { labels: { color: textColor, usePointStyle: true, padding: 16 } } },
      scales: {
        x: { ticks: { color: textColor }, grid: { display: false } },
        y: { beginAtZero: true, ticks: { color: textColor, stepSize: 1 }, grid: { color: gridColor } }
      },
      responsive: true,
      maintainAspectRatio: false,
    };
  }
}
