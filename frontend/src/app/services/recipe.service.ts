import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface RecipeSuggestion {
  recipe: string;
  tagline: string;
  fruit: string;
  benefits?: string[];
  color?: string;
  dietary?: string[];
  meal_type?: string;
  cuisine?: string;
  suggested_pairings?: string[];
}

@Injectable({ providedIn: 'root' })
export class RecipeService {
  constructor(private http: HttpClient) {}

  generateRecipe(
    fruits: string[],
    dietary?: string[],
    cuisine?: string,
    mealType?: string
  ): Observable<RecipeSuggestion> {
    return this.http.post<RecipeSuggestion>('/recipes/generate', {
      fruits,
      dietary_preferences: dietary || [],
      cuisine_type: cuisine || null,
      meal_type: mealType || null
    });
  }
}
