import { Component, input, output, signal } from '@angular/core';
import { Recipe } from '../../../../../../models/recipe_models';

@Component({
  selector: 'app-recipe-stats',
  imports: [],
  template: ` <div class="recipe-card stats-card">
    <div class="stats-grid">
      @for (stat of recipeStats(); track stat.label) {
      <div class="stat-item">
        <div class="stat-icon {{ stat.bgColor }}-bg">
          <svg
            class="icon {{ stat.iconColor }}-icon"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              [attr.d]="stat.icon"
            />
          </svg>
        </div>
        <p class="stat-label">{{ stat.label }}</p>
        <p class="stat-value">{{ stat.value }}</p>
      </div>
      }
    </div>

    <!-- Scale Recipe -->
    <div class="scale-recipe-section">
      <label class="scale-label">Scale Recipe:</label>
      <div class="scale-controls">
        <button
          (click)="decreaseServings()"
          class="scale-btn decrease-btn"
          [disabled]="scaledServings() <= 1"
        >
          -
        </button>
        <span class="servings-count">{{ scaledServings() }}</span>
        <button (click)="increaseServings()" class="scale-btn increase-btn">+</button>
      </div>
    </div>
  </div>`,
  styleUrl: './recipe-stats.scss',
})
export class RecipeStats {
  recipe = input.required<Recipe>();
  servingsChanged = output<number>();

  scaledServings = signal(1);

  recipeStats = signal<any[]>([]);

  ngOnInit() {
    this.scaledServings.set(this.recipe().servings || 1);
    this.updateStats();
  }

  private updateStats() {
    this.recipeStats.set([
      {
        label: 'Prep Time',
        value: `${this.recipe().prepTimeMinutes} min`,
        icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
        bgColor: 'orange',
        iconColor: 'orange',
      },
      {
        label: 'Cook Time',
        value: `${this.recipe().cookTimeMinutes} min`,
        icon: 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z',
        bgColor: 'red',
        iconColor: 'red',
      },
      {
        label: 'Servings',
        value: this.scaledServings().toString(),
        icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
        bgColor: 'blue',
        iconColor: 'blue',
      },
    ]);
  }

  increaseServings(): void {
    this.scaledServings.update((s) => s + 1);
    this.servingsChanged.emit(this.scaledServings());
    this.updateStats();
  }

  decreaseServings(): void {
    if (this.scaledServings() > 1) {
      this.scaledServings.update((s) => s - 1);
      this.servingsChanged.emit(this.scaledServings());
      this.updateStats();
    }
  }
}
