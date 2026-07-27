import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface DiseaseInfo {
  severity: string;
  category: string;
  synonyms: string[];
}

export interface Recommendation {
  class: string;
  reason: string;
  score: number;
  evidence?: string;
  sample?: string;
}

export interface RecommendResult {
  recommendations: Recommendation[];
  disease: string;
  normalized: string;
  category: string;
  severity: string;
  total_candidates: number;
  filtered_count: number;
}

export interface NlpEntity {
  diseases: string[];
  fruits: string[];
  symptoms: string[];
}

@Injectable({ providedIn: 'root' })
export class RecommendService {
  constructor(private http: HttpClient) {}

  listDiseases(): Observable<{ diseases: string[]; total: number }> {
    return this.http.get<{ diseases: string[]; total: number }>('/api/recommend/diseases');
  }

  getDiseaseInfo(disease: string): Observable<{ disease: string; info: DiseaseInfo }> {
    return this.http.get<{ disease: string; info: DiseaseInfo }>(`/api/recommend/diseases/${disease}`);
  }

  recommend(disease: string, have: string[] = []): Observable<RecommendResult> {
    return this.http.post<RecommendResult>('/api/recommend', { disease, have });
  }

  recommendNatural(text: string): Observable<RecommendResult & { entities: NlpEntity }> {
    return this.http.post<RecommendResult & { entities: NlpEntity }>('/api/recommend/natural', { text });
  }

  extractNlp(text: string): Observable<NlpEntity> {
    return this.http.post<NlpEntity>('/api/nlp/extract', { text });
  }
}
