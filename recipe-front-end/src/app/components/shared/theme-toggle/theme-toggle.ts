import { Component, inject } from '@angular/core';
import { ThemeService } from '../../../services/theme.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-theme-toggle',
  imports: [CommonModule],
  templateUrl: './theme-toggle.html',
  styleUrl: './theme-toggle.scss',
})
export class ThemeToggle {
  themeService = inject(ThemeService);
  dropDownOpen = false;

  toggleDropdown(): void {
    this.dropDownOpen = !this.dropDownOpen;
  }

  selectTheme(theme: 'light' | 'dark' | 'system'): void {
    this.themeService.setTheme(theme);
    this.dropDownOpen = false;
  }

  onDocumentClick(event: Event) {
    const target = event.target as HTMLElement;
    if (!target.closest('app-theme-toggle')) {
      this.dropDownOpen = false;
    }
  }
}
