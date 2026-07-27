import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-meal-planner',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, MatIconModule],
  template: `
    <div class="page-hero">
      <div class="hero-bg">
        <div class="glass-overlay"></div>
        <div class="floating-shapes">
          <div class="shape s1"></div>
          <div class="shape s2"></div>
          <div class="shape s3"></div>
        </div>
      </div>
      <div class="hero-content">
        <div class="hero-icon">
          <mat-icon>restaurant_menu</mat-icon>
        </div>
        <h1 class="gradient-text">Meal Planner</h1>
        <p class="hero-subtitle">AI-optimized meal plans tailored to your health goals</p>
      </div>
    </div>

    <div class="page-section">
      <div class="premium-card">
        <div class="form-row">
          <div class="field">
            <label>Number of Days</label>
            <input type="number" [(ngModel)]="days" min="1" max="30" class="premium-input">
          </div>
        </div>

        <div class="form-row">
          <div class="field">
            <label>Health Goals</label>
            <div class="chip-group">
              <button *ngFor="let g of goals" class="chip" [class.active]="selectedGoals.includes(g)" (click)="toggle(selectedGoals, g)">{{ g.replace('_',' ') }}</button>
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="field">
            <label>Dietary Preferences</label>
            <div class="chip-group">
              <button *ngFor="let p of dietaryPrefs" class="chip" [class.active]="selectedPrefs.includes(p)" (click)="toggle(selectedPrefs, p)">{{ p.replace('_',' ') }}</button>
            </div>
          </div>
        </div>

        <button class="btn-primary" (click)="generate()" [disabled]="loading">
          {{ loading ? 'Generating...' : 'Generate Meal Plan' }}
        </button>
      </div>

      <div *ngIf="error" class="error-banner">{{ error }}</div>

      <div *ngIf="loading" class="loading-section">
        <div class="spinner"></div>
      </div>

      <div *ngIf="planData" class="results">
        <div class="hero-stats">
          <div class="stat-item" *ngFor="let s of summary">
            <div class="stat-value">{{ s.val }}</div>
            <div class="stat-label">{{ s.lbl }}</div>
          </div>
        </div>

        <div class="day-card" *ngFor="let day of planData.days; let i = index">
          <h3><mat-icon>calendar_today</mat-icon> {{ day.date }}</h3>
          <div class="meal-grid">
            <div class="meal-card" *ngFor="let meal of day.meals">
              <div class="meal-header">
                <span class="meal-type">{{ meal.type }}</span>
                <span class="meal-fruit">{{ meal.fruit }}</span>
              </div>
              <div class="meal-recipe">{{ meal.recipe?.title || meal.fruit + ' serving' }}</div>
              <div class="meal-nutrition">
                <span *ngFor="let n of entries(meal.nutrition)" class="nut-badge">{{ n[0] }}: {{ n[1] }}</span>
              </div>
            </div>
          </div>
        </div>

        <div *ngIf="shopping?.length" class="shopping-section">
          <h3>Shopping List</h3>
          <div class="shopping-grid">
            <div class="shop-item" *ngFor="let item of shopping">
              <span class="shop-name">{{ item.fruit }}</span>
              <span class="shop-qty">{{ item.quantity }} {{ item.unit }}</span>
              <span class="shop-season">{{ item.season }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .form-row { margin-bottom: 20px; }
    .field label { display: block; font-size: .85rem; color: var(--text-muted); margin-bottom: 10px; font-weight: 500; letter-spacing: .3px; }
    .premium-input { width: 100px; }
    .day-card { background: var(--surface); border-radius: 20px; padding: 28px; margin-bottom: 20px; border: 1px solid var(--border-color); }
    .day-card h3 { display: flex; align-items: center; gap: 8px; font-size: 1.05rem; color: var(--text-primary); margin-bottom: 18px; }
    .meal-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(260px,1fr)); gap: 14px; }
    .meal-card { background: rgba(255,255,255,.03); border-radius: 14px; padding: 18px; border-left: 3px solid var(--primary); }
    .meal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .meal-type { font-size: .7rem; text-transform: uppercase; letter-spacing: 1px; color: var(--primary); font-weight: 700; }
    .meal-fruit { font-size: 1rem; font-weight: 700; }
    .meal-recipe { font-size: .85rem; color: var(--text-muted); margin-bottom: 10px; }
    .meal-nutrition { display: flex; flex-wrap: wrap; gap: 6px; }
    .nut-badge { font-size: .7rem; background: rgba(255,255,255,.06); padding: 3px 10px; border-radius: 6px; color: var(--text-secondary); }
    .shopping-section { margin-top: 28px; }
    .shopping-section h3 { font-size: 1.1rem; margin-bottom: 16px; }
    .shopping-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(220px,1fr)); gap: 12px; }
    .shop-item { background: var(--surface); border-radius: 12px; padding: 16px 20px; border: 1px solid var(--border-color); display: flex; flex-direction: column; gap: 4px; }
    .shop-name { font-weight: 600; font-size: .95rem; }
    .shop-qty { font-size: .8rem; color: var(--text-muted); }
    .shop-season { font-size: .75rem; color: var(--accent); }
  `]
})
export class MealPlannerComponent implements OnInit {
  days = 7;
  goals: string[] = [];
  dietaryPrefs = ['vegan','low_carb','high_protein','low_sugar','keto','gluten_free'];
  selectedGoals: string[] = [];
  selectedPrefs: string[] = [];
  loading = false;
  error = '';
  planData: any = null;
  shopping: any[] = [];
  summary: {lbl:string;val:string}[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.http.get<any>('/api/meal-planner/goals').subscribe({
      next: r => this.goals = Object.keys(r.goals || {}),
      error: () => this.goals = ['weight_loss','muscle_build','immunity','energy_boost','heart_health','digestion','detox']
    });
  }

  toggle(arr: string[], val: string) {
    const i = arr.indexOf(val);
    i >= 0 ? arr.splice(i,1) : arr.push(val);
  }

  generate() {
    this.loading = true;
    this.error = '';
    this.http.post<any>('/api/meal-planner/generate', {
      days: this.days, goals: this.selectedGoals, dietary_preferences: this.selectedPrefs
    }).subscribe({
      next: r => {
        this.planData = r.meal_plan;
        this.shopping = r.shopping_list || [];
        this.summary = Object.entries(r.meal_plan?.summary?.average_daily_nutrition || {}).map(([k,v]) => ({
          lbl: k.replace(/_/g,' '), val: typeof v === 'number' ? v.toFixed(1) : String(v)
        }));
        this.loading = false;
      },
      error: e => {
        this.error = 'Failed to generate meal plan. Make sure the backend is running.';
        this.loading = false;
      }
    });
  }

  entries(obj: any): [string,any][] { return Object.entries(obj || {}); }
}
