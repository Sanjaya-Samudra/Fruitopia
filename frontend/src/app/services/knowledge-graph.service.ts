import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class KnowledgeGraphService {
  constructor(private http: HttpClient) {}

  getStats(): Observable<any> {
    return this.http.get<any>('/knowledge-graph/stats');
  }

  getFruitEvidence(name: string): Observable<any> {
    return this.http.get<any>(`/knowledge-graph/fruit/${name}`);
  }

  getDiseaseEvidence(tag: string): Observable<any> {
    return this.http.get<any>(`/knowledge-graph/disease/${tag}`);
  }

  search(query: string): Observable<any> {
    return this.http.get<any>('/knowledge-graph/search', { params: { q: query } });
  }

  getRecommendations(condition?: string, nutrient?: string): Observable<any> {
    let params: any = {};
    if (condition) params.condition = condition;
    if (nutrient) params.nutrient = nutrient;
    return this.http.get<any>('/knowledge-graph/recommendations', { params });
  }
}
