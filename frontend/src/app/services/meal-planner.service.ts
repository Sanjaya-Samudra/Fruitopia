import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface MealPlanDay {
  date: string;
  meals: any[];
  total_nutrition: any;
}

export interface MealPlan {
  days: MealPlanDay[];
  summary: any;
}

export interface ShoppingItem {
  fruit: string;
  quantity: number;
  unit: string;
  season: string;
  color: string;
}

@Injectable({ providedIn: 'root' })
export class MealPlannerService {
  constructor(private http: HttpClient) {}

  generatePlan(params: any): Observable<{ meal_plan: MealPlan; shopping_list: ShoppingItem[] }> {
    return this.http.post<{ meal_plan: MealPlan; shopping_list: ShoppingItem[] }>('/meal-planner/generate', params);
  }

  getGoals(): Observable<any> {
    return this.http.get<any>('/meal-planner/goals');
  }

  getFruits(): Observable<any> {
    return this.http.get<any>('/meal-planner/fruits');
  }
}
