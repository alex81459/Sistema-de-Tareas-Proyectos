import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable, catchError, finalize, map, shareReplay, switchMap, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

let isRefreshing = false;
let refreshTokenRequest$: Observable<string> | null = null;

function agregarToken(request: HttpRequest<any>, token: string): HttpRequest<any> {
  return request.clone({
    setHeaders: { Authorization: `Bearer ${token}` }
  });
}

function obtenerRefreshCompartido(authService: AuthService): Observable<string> {
  if (!refreshTokenRequest$) {
    isRefreshing = true;
    refreshTokenRequest$ = authService.actualizarToken().pipe(
      map(tokens => tokens.access_token),
      finalize(() => {
        isRefreshing = false;
        refreshTokenRequest$ = null;
      }),
      shareReplay(1)
    );
  }

  return refreshTokenRequest$;
}

export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<any>, next: HttpHandlerFn) => {
  const authService = inject(AuthService);

  if (req.url.includes('iniciar-sesion') || req.url.includes('registrar') || req.url.includes('actualizar-token')) {
    return next(req);
  }

  const token = authService.getAccessToken();
  let authReq = req;

  if (token) {
    authReq = agregarToken(req, token);
  }

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401 && authService.getAccessToken()) {
        return obtenerRefreshCompartido(authService).pipe(
          switchMap((nuevoAccessToken) => {
            const retryReq = agregarToken(req, nuevoAccessToken);
            return next(retryReq);
          }),
          catchError((refreshError) => {
            if (isRefreshing || refreshTokenRequest$ === null) {
              authService.cerrarSesion();
            }
            return throwError(() => refreshError);
          })
        );
      }
      return throwError(() => error);
    })
  );
};
