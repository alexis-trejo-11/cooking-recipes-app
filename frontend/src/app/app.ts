import { Component, OnInit, signal } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { Header } from './components/shared/header/header';
import { Footer } from './components/shared/footer/footer';
import { filter } from 'rxjs';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Header, Footer],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {
  protected readonly title = signal('recipe-front-end');
  showHeaderFooter = true;

  constructor(private router: Router, private authService: AuthService) {
    this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe((event: NavigationEnd) => {
        this.showHeaderFooter =
          !event.url.startsWith('/dashboard') &&
          !event.url.startsWith('/login') &&
          !event.url.startsWith('/signup') &&
          !event.url.startsWith('/rate-limiter');
      });
  }

  ngOnInit() {
    // Inicializar manualmente el AuthService después de que la app esté lista
    this.authService.initialize().then((authenticated) => {
      console.log('AuthService inicializado, usuario autenticado:', authenticated);
    });
  }
}
