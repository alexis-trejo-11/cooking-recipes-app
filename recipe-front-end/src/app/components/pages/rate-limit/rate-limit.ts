import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { Subject, interval, takeUntil } from 'rxjs';

@Component({
  selector: 'app-rate-limit',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './rate-limit.html',
  styleUrls: ['./rate-limit.scss'],
})
export class RateLimit implements OnInit, OnDestroy {
  private router = inject(Router);

  private destroy$ = new Subject<void>();

  countdown = signal(60); // 60 seconds default
  errorMessage = signal('Too many requests');
  isCounting = signal(false);

  ngOnInit() {
    const navigation = this.router.currentNavigation();
    interface RateLimitState {
      resetTime?: number;
      errorMessage?: string;
    }
    const state: RateLimitState =
      (navigation?.extras?.state as RateLimitState) ?? (history.state as RateLimitState);

    if (state) {
      const resetTime = state.resetTime ?? 60000;
      this.countdown.set(Math.ceil(resetTime / 1000));
      this.errorMessage.set(state.errorMessage ?? 'Too many requests');
    }

    this.startCountdown();
  }
  private startCountdown() {
    this.isCounting.set(true);

    interval(1000)
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        const current = this.countdown();
        if (current > 1) {
          this.countdown.set(current - 1);
        } else {
          this.isCounting.set(false);
        }
      });
  }

  tryAgain() {
    if (!this.isCounting()) {
      this.router.navigate(['/']);
    }
  }

  goHome() {
    this.router.navigate(['/']);
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
