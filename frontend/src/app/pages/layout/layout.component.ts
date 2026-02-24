import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { ThemeService } from '../../core/services/theme.service';
import { ButtonModule } from 'primeng/button';
import { AvatarModule } from 'primeng/avatar';
import { ChipModule } from 'primeng/chip';
import { TooltipModule } from 'primeng/tooltip';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { ToastModule } from 'primeng/toast';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, ButtonModule, AvatarModule, ChipModule, TooltipModule, ConfirmDialogModule, ToastModule],
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.scss']
})
export class LayoutComponent {
  sidebarAbierto = false;

  constructor(public authService: AuthService, public themeService: ThemeService) {}

  cerrarSesion(): void {
    this.authService.cerrarSesion();
  }
}
