import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class RecommendService {
  constructor(private http: HttpClient) {}

  listDiseases(): Observable<any> {
    return this.http.get('/recommend/diseases');
  }

  recommend(disease: string, have: string[]): Observable<any> {
    return this.http.post('/recommend', { disease, have });
  }
}
