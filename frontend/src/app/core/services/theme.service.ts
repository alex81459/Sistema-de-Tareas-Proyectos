import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly STORAGE_KEY = 'darkMode';
  private _darkMode = new BehaviorSubject<boolean>(this.cargarPreferencia());

  darkMode$ = this._darkMode.asObservable();

  get isDark(): boolean {
    return this._darkMode.value;
  }

  constructor() {
    this.aplicarTema(this._darkMode.value);
  }

  toggle(): void {
    const nuevo = !this._darkMode.value;
    this._darkMode.next(nuevo);
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(nuevo));
    this.aplicarTema(nuevo);
  }

  private cargarPreferencia(): boolean {
    const stored = localStorage.getItem(this.STORAGE_KEY);
    if (stored !== null) {
      return JSON.parse(stored);
    }
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false;
  }

  private aplicarTema(dark: boolean): void {
    document.body.classList.toggle('dark-theme', dark);
  }
}
