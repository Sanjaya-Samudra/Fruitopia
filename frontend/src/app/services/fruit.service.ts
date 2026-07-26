import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface FruitSummary {
  name: string;
  slug: string;
  scientificName: string;
  description: string;
  origin: string;
  family: string;
  health_benefits: string[];
  fun_facts: string[];
  colors: string[];
  season: string;
  calories: number;
}

export interface FruitDetail {
  fruitName: string;
  scientificName: string;
  description: string;
  origin: string;
  family: string;
  healthBenefits: string[];
  nutritionalFacts: any;
  appearance: any;
  storageAndShelfLife: any;
  funFacts: string[];
  warnings: string[];
  [key: string]: any;
}

export interface NutritionInfo {
  fruit: string;
  nutrition: any;
  health_benefits: string[];
}

export interface UsdaNutrition {
  fruit: string;
  detail?: any;
  source: string;
  search_summary?: any;
}

export interface SearchResult {
  name: string;
  slug: string;
  score: number;
  description: string;
}

export interface SeasonalityInfo {
  name: string;
  slug: string;
  season: string;
  origin: string;
}

@Injectable({ providedIn: 'root' })
export class FruitService {
  constructor(private http: HttpClient) {}

  listFruits(): Observable<{ fruits: FruitSummary[]; total: number }> {
    return this.http.get<{ fruits: FruitSummary[]; total: number }>('/fruits');
  }

  getFruit(slug: string): Observable<FruitDetail> {
    return this.http.get<FruitDetail>(`/fruits/${slug}`);
  }

  getNutrition(slug: string): Observable<NutritionInfo> {
    return this.http.get<NutritionInfo>(`/fruits/${slug}/nutrition`);
  }

  getUsdaData(slug: string): Observable<UsdaNutrition> {
    return this.http.get<UsdaNutrition>(`/fruits/${slug}/usda`);
  }

  search(query: string): Observable<{ query: string; results: SearchResult[] }> {
    return this.http.get<{ query: string; results: SearchResult[] }>(`/fruits/search?q=${encodeURIComponent(query)}`);
  }

  searchByBenefit(benefit: string): Observable<any> {
    return this.http.get(`/fruits/search/benefit?b=${encodeURIComponent(benefit)}`);
  }

  getSeasonality(): Observable<{ seasonality: SeasonalityInfo[] }> {
    return this.http.get<{ seasonality: SeasonalityInfo[] }>('/fruits/seasonality');
  }
}
