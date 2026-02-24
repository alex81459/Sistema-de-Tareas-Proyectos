import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

let isRefreshing = false;

export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<any>, next: HttpHandlerFn) => {
  const authService = inject(AuthService);

  if (req.url.includes('iniciar-sesion') || req.url.includes('registrar') || req.url.includes('actualizar-token')) {
    return next(req);
  }

  const token = authService.getAccessToken();
  let authReq = req;

  if (token) {
    authReq = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    });
  }

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401 && !isRefreshing && authService.getRefreshToken()) {
        isRefreshing = true;
        return authService.actualizarToken().pipe(
          switchMap((tokens) => {
            isRefreshing = false;
            const retryReq = req.clone({
              setHeaders: { Authorization: `Bearer ${tokens.access_token}` }
            });
            return next(retryReq);
          }),
          catchError((refreshError) => {
            isRefreshing = false;
            authService.cerrarSesion();
            return throwError(() => refreshError);
          })
        );
      }
      return throwError(() => error);
    })
  );
};
