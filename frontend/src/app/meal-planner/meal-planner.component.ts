import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MealPlannerService, MealPlan, ShoppingItem } from '../services/meal-planner.service';

@Component({
  selector: 'app-meal-planner',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page">
      <div class="page-header">
        <h1>Meal Planner</h1>
        <p>AI-optimized meal plans based on your health goals</p>
      </div>

      <div class="planner-form">
        <div class="form-grid">
          <div class="field">
            <label>Days</label>
            <input type="number" [(ngModel)]="days" min="1" max="30">
          </div>
          <div class="field">
            <label>Goals <small>(select all that apply)</small></label>
            <div class="chip-group">
              <button *ngFor="let g of goals" class="chip" [class.active]="selectedGoals.includes(g)" (click)="toggleGoal(g)">{{ g }}</button>
            </div>
          </div>
          <div class="field">
            <label>Dietary Preferences</label>
            <div class="chip-group">
              <button *ngFor="let p of dietaryPrefs" class="chip" [class.active]="selectedPrefs.includes(p)" (click)="togglePref(p)">{{ p }}</button>
            </div>
          </div>
        </div>
        <button class="btn-primary" (click)="generatePlan()" [disabled]="loading">
          {{ loading ? 'Generating...' : 'Generate Meal Plan' }}
        </button>
      </div>

      <div *ngIf="plan" class="plan-result">
        <h2>Your {{ days }}-Day Meal Plan</h2>
        <div class="summary-cards">
          <div class="summary-card" *ngFor="let item of summaryItems">
            <span class="val">{{ item.value }}</span>
            <span class="lbl">{{ item.label }}</span>
          </div>
        </div>

        <div class="days" *ngFor="let day of plan.days; let i = index">
          <h3>{{ day.date }}</h3>
          <div class="meal-grid">
            <div class="meal-card" *ngFor="let meal of day.meals">
              <div class="meal-type">{{ meal.type | titlecase }}</div>
              <div class="meal-fruit">{{ meal.fruit }}</div>
              <div class="meal-recipe">{{ meal.recipe?.title }}</div>
              <div class="meal-nutrition">
                <span *ngFor="let n of getEntries(meal.nutrition)" class="nut">{{ fmt(n[0]) }}: {{ n[1] }}</span>
              </div>
            </div>
          </div>
        </div>

        <div *ngIf="shoppingList?.length" class="shopping">
          <h3>Shopping List</h3>
          <div class="shopping-grid">
            <div class="shop-item" *ngFor="let item of shoppingList">
              <span class="item-fruit">{{ item.fruit }}</span>
              <span class="item-qty">{{ item.quantity }} {{ item.unit }}</span>
              <span class="item-season">{{ item.season }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .planner-form { background: var(--surface); border-radius: 16px; padding: 28px; margin-bottom: 32px; }
    .form-grid { display: grid; grid-template-columns: 1fr 2fr 2fr; gap: 24px; margin-bottom: 20px; }
    .field label { display: block; font-size: .85rem; color: var(--text-muted); margin-bottom: 8px; }
    .chip-group { display: flex; flex-wrap: wrap; gap: 8px; }
    .chip { padding: 6px 14px; border-radius: 20px; border: 1px solid var(--border); background: transparent; color: var(--text); cursor: pointer; font-size: .8rem; }
    .chip.active { background: var(--gradient-primary); border-color: transparent; color: #fff; }
    .summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px,1fr)); gap: 16px; margin: 20px 0; }
    .summary-card { background: var(--surface); border-radius: 12px; padding: 16px; text-align: center; }
    .summary-card .val { display: block; font-size: 1.4rem; font-weight: 700; color: var(--primary); }
    .summary-card .lbl { font-size: .75rem; color: var(--text-muted); }
    .meal-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px,1fr)); gap: 16px; }
    .meal-card { background: var(--surface); border-radius: 12px; padding: 16px; border-left: 3px solid var(--primary); }
    .meal-type { font-size: .7rem; text-transform: uppercase; letter-spacing: 1px; color: var(--primary); font-weight: 600; }
    .meal-fruit { font-size: 1.1rem; font-weight: 600; margin: 6px 0; }
    .meal-nutrition { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
    .nut { font-size: .7rem; background: rgba(255,255,255,.05); padding: 2px 8px; border-radius: 4px; }
    .shopping-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px,1fr)); gap: 12px; }
    .shop-item { background: var(--surface); border-radius: 10px; padding: 16px; display: flex; flex-direction: column; }
    .item-fruit { font-weight: 600; }
    .item-qty { font-size: .8rem; color: var(--text-muted); }
    .item-season { font-size: .75rem; color: var(--primary); }
    @media (max-width:768px) { .form-grid { grid-template-columns: 1fr; } }
  `]
})
export class MealPlannerComponent implements OnInit {
  days = 7;
  goals: string[] = [];
  dietaryPrefs = ['vegan', 'low_carb', 'high_protein', 'low_sugar', 'keto', 'gluten_free'];
  selectedGoals: string[] = [];
  selectedPrefs: string[] = [];
  loading = false;
  plan: MealPlan | null = null;
  shoppingList: ShoppingItem[] | null = null;
  summaryItems: { label: string; value: string }[] = [];

  constructor(private service: MealPlannerService) {}

  ngOnInit() {
    this.service.getGoals().subscribe(r => this.goals = Object.keys(r.goals));
  }

  toggleGoal(g: string) {
    const i = this.selectedGoals.indexOf(g);
    i >= 0 ? this.selectedGoals.splice(i, 1) : this.selectedGoals.push(g);
  }

  togglePref(p: string) {
    const i = this.selectedPrefs.indexOf(p);
    i >= 0 ? this.selectedPrefs.splice(i, 1) : this.selectedPrefs.push(p);
  }

  fmt(k: string): string { return k.replace(/_/g, ' '); }

  getEntries(obj: any): [string, any][] { return Object.entries(obj || {}); }

  generatePlan() {
    this.loading = true;
    this.service.generatePlan({
      days: this.days,
      goals: this.selectedGoals,
      dietary_preferences: this.selectedPrefs,
    }).subscribe(r => {
      this.plan = r.meal_plan;
      this.shoppingList = r.shopping_list;
      this.summaryItems = Object.entries(r.meal_plan.summary.average_daily_nutrition || {}).map(([k, v]) => ({
        label: k.replace(/_/g, ' '),
        value: typeof v === 'number' ? v.toFixed(1) : String(v),
      }));
      this.loading = false;
    });
  }
}
