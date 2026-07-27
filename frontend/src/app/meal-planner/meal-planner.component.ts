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
    <div class="page-container">
      <div class="page-title">
        <h1><span class="gradient-text">Meal Planner</span></h1>
        <p class="subtitle">AI-optimized meal plans tailored to your health goals</p>
      </div>

      <div class="planner-card">
        <div class="form-row">
          <div class="field">
            <label>Number of Days</label>
            <input type="number" [(ngModel)]="days" min="1" max="30" class="input">
          </div>
        </div>

        <div class="form-row">
          <div class="field">
            <label>Health Goals</label>
            <div class="chip-row">
              <button *ngFor="let g of goals" class="chip" [class.active]="selectedGoals.includes(g)" (click)="toggle(selectedGoals, g)">{{ g.replace('_',' ') }}</button>
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="field">
            <label>Dietary Preferences</label>
            <div class="chip-row">
              <button *ngFor="let p of dietaryPrefs" class="chip" [class.active]="selectedPrefs.includes(p)" (click)="toggle(selectedPrefs, p)">{{ p.replace('_',' ') }}</button>
            </div>
          </div>
        </div>

        <button class="btn-primary" (click)="generate()" [disabled]="loading">
          {{ loading ? 'Generating...' : 'Generate Meal Plan' }}
        </button>
      </div>

      <div *ngIf="error" class="error-banner">{{ error }}</div>

      <div *ngIf="planData" class="results">
        <div class="summary-row">
          <div class="summary-card" *ngFor="let s of summary">
            <div class="summary-val">{{ s.val }}</div>
            <div class="summary-lbl">{{ s.lbl }}</div>
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
    .planner-card { background: var(--surface); border-radius: 20px; padding: 32px; margin-bottom: 24px; border: 1px solid var(--border-color); }
    .form-row { margin-bottom: 20px; }
    .field label { display: block; font-size: .85rem; color: var(--text-muted); margin-bottom: 10px; font-weight: 500; letter-spacing: .3px; }
    .input { width: 100px; padding: 10px 14px; border-radius: 10px; border: 1px solid var(--border-color); background: rgba(255,255,255,.05); color: var(--text-primary); font-size: 1rem; }
    .chip-row { display: flex; flex-wrap: wrap; gap: 8px; }
    .chip { padding: 8px 18px; border-radius: 50px; border: 1px solid var(--border-color); background: transparent; color: var(--text-secondary); cursor: pointer; font-size: .82rem; transition: all .2s; }
    .chip:hover { border-color: var(--primary); color: var(--text-primary); }
    .chip.active { background: var(--gradient-primary); border-color: transparent; color: #fff; font-weight: 600; }
    .error-banner { background: rgba(239,68,68,.15); border: 1px solid rgba(239,68,68,.3); border-radius: 12px; padding: 14px 20px; color: #fca5a5; margin-bottom: 20px; }
    .summary-row { display: grid; grid-template-columns: repeat(auto-fit,minmax(120px,1fr)); gap: 12px; margin-bottom: 28px; }
    .summary-card { background: var(--surface); border-radius: 14px; padding: 20px 16px; text-align: center; border: 1px solid var(--border-color); }
    .summary-val { font-size: 1.4rem; font-weight: 800; background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .summary-lbl { font-size: .7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; margin-top: 4px; }
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
