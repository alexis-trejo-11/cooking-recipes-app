import { Component, inject, signal, ChangeDetectorRef, afterNextRender } from '@angular/core';
import {
  NavigationEnd,
  NavigationStart,
  Router,
  RouterOutlet,
  NavigationCancel,
  NavigationError,
} from '@angular/router';
import { Header } from './shared/header/header';
import { Footer } from './shared/footer/footer';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Header, Footer],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  protected readonly title = signal('recipe-front-end');
  private cdr = inject(ChangeDetectorRef);
  private router = inject(Router);

  constructor() {
    this.router.events.subscribe((event) => {
      console.log('🔵 [ROUTER EVENT]', event.constructor.name, event);

      if (event instanceof NavigationStart) {
        console.log('🟡 [NAV START] From:', this.router.url, 'To:', event.url);
      }

      if (event instanceof NavigationEnd) {
        console.log('🟢 [NAV END] Current URL:', event.url);
        this.cdr.detectChanges();
      }

      if (event instanceof NavigationCancel) {
        console.log('🟠 [NAV CANCEL]', event.url, 'Reason:', event.reason);
      }

      if (event instanceof NavigationError) {
        console.error('🔴 [NAV ERROR]', event.url, 'Error:', event.error);
      }
    });
  }

  onActivate(component: any) {
    console.log('⚡ [ACTIVATE] Component:', component.constructor.name);
    this.cdr.detectChanges();
  }
}
