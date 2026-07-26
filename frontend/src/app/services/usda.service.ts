import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class UsdaService {
  constructor(private http: HttpClient) {}

  searchFood(query: string): Observable<any> {
    return this.http.get(`/usda/search?q=${encodeURIComponent(query)}`);
  }

  getFruitNutrition(fruitName: string): Observable<any> {
    return this.http.get(`/usda/fruit/${encodeURIComponent(fruitName)}`);
  }
}
