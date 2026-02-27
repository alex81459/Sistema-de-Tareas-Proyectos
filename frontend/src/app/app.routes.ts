import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { guestGuard } from './core/guards/guest.guard';
import { adminGuard, gestorGuard } from './core/guards/admin.guard';

export const routes: Routes = [
  {
    path: 'iniciar-sesion',
    canActivate: [guestGuard],
    loadComponent: () => import('./pages/auth/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'registrar',
    canActivate: [guestGuard],
    loadComponent: () => import('./pages/auth/registro/registro.component').then(m => m.RegistroComponent)
  },
  {
    path: 'app',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/layout/layout.component').then(m => m.LayoutComponent),
    children: [
      {
        path: 'panel',
        loadComponent: () => import('./pages/panel/panel.component').then(m => m.PanelComponent)
      },
      {
        path: 'proyectos',
        loadComponent: () => import('./pages/proyectos/lista-proyectos/lista-proyectos.component').then(m => m.ListaProyectosComponent)
      },
      {
        path: 'proyectos/:id',
        loadComponent: () => import('./pages/proyectos/detalle-proyecto/detalle-proyecto.component').then(m => m.DetalleProyectoComponent)
      },
      {
        path: 'tareas',
        loadComponent: () => import('./pages/tareas/lista-tareas/lista-tareas.component').then(m => m.ListaTareasComponent)
      },
      {
        path: 'tareas/kanban',
        loadComponent: () => import('./pages/tareas/tablero-kanban/tablero-kanban.component').then(m => m.TableroKanbanComponent)
      },
      {
        path: 'etiquetas',
        loadComponent: () => import('./pages/etiquetas/lista-etiquetas/lista-etiquetas.component').then(m => m.ListaEtiquetasComponent)
      },
      {
        path: 'usuarios',
        canActivate: [gestorGuard],
        loadComponent: () => import('./pages/usuarios/lista-usuarios/lista-usuarios.component').then(m => m.ListaUsuariosComponent)
      },
      {
        path: 'auditoria',
        canActivate: [adminGuard],
        loadComponent: () => import('./pages/auditoria/auditoria.component').then(m => m.AuditoriaComponent)
      },
      { path: '', redirectTo: 'panel', pathMatch: 'full' }
    ]
  },
  { path: '', redirectTo: 'iniciar-sesion', pathMatch: 'full' },
  { path: '**', redirectTo: 'iniciar-sesion' }
];
