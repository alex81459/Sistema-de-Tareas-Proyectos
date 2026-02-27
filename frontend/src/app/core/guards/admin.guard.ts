import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';

export const adminGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.estaAutenticado && authService.esAdmin) {
    return true;
  }
  router.navigate(['/app/panel']);
  return false;
};

export const gestorGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.estaAutenticado && authService.puedeVerUsuarios) {
    return true;
  }
  router.navigate(['/app/panel']);
  return false;
};

export const escrituraGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.estaAutenticado && authService.puedeEscribir) {
    return true;
  }
  router.navigate(['/app/panel']);
  return false;
};
