import { effect, Injectable, inject, PLATFORM_ID, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

type Theme = 'light' | 'dark' | 'system';

@Injectable({
  providedIn: 'root',
})
export class ThemeService {
  private readonly THEME_KEY = 'theme-preference';
  private platformId = inject(PLATFORM_ID);

  theme = signal<Theme>(this.getInitialTheme());
  isDark = signal<boolean>(false);

  constructor() {
    this.applyTheme();

    // Solo ejecutar effect en el cliente
    if (isPlatformBrowser(this.platformId)) {
      effect(() => {
        const theme = this.theme();
        localStorage.setItem(this.THEME_KEY, theme);
        this.applyTheme();
      });

      // Solo en el cliente
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (this.theme() === 'system') {
          this.applyTheme();
        }
      });
    }
  }

  private getInitialTheme(): Theme {
    // En el servidor, siempre retornar 'system'
    if (!isPlatformBrowser(this.platformId)) {
      return 'system';
    }

    return (localStorage.getItem(this.THEME_KEY) as Theme) || 'system';
  }

  private getSystemTheme(): Theme {
    if (!isPlatformBrowser(this.platformId)) {
      return 'light'; // Default en servidor
    }

    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  private applyTheme(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    const theme = this.theme();
    const effectiveTheme = theme === 'system' ? this.getSystemTheme() : theme;

    this.isDark.set(effectiveTheme === 'dark');

    if (effectiveTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }

  setTheme(theme: Theme): void {
    this.theme.set(theme);
  }

  toggleTheme(): void {
    const current = this.theme();
    if (current === 'system') {
      this.setTheme(this.getSystemTheme() === 'dark' ? 'light' : 'dark');
    } else {
      this.setTheme(current === 'light' ? 'dark' : 'light');
    }
  }
}
