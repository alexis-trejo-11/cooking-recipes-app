import { Component, signal } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { Header } from './components/shared/header/header';
import { Footer } from './components/shared/footer/footer';
import { filter } from 'rxjs';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Header, Footer],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  protected readonly title = signal('recipe-front-end');
  showHeaderFooter = true;

  constructor(private router: Router) {
    this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe((event: NavigationEnd) => {
        this.showHeaderFooter =
          !event.url.startsWith('/dashboard') &&
          !event.url.startsWith('/login') &&
          !event.url.startsWith('/signup');
      });
  }
}
