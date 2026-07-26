import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class FruitCultureService {
  constructor(private http: HttpClient) {}

  getCultures(): Observable<any> {
    return this.http.get<any>('/culture/fruits');
  }

  getFruitDetail(name: string): Observable<any> {
    return this.http.get<any>(`/culture/fruit/${name}`);
  }

  getGlobalStats(): Observable<any> {
    return this.http.get<any>('/culture/global-stats');
  }

  getSeasonal(hemisphere?: string, season?: string): Observable<any> {
    let params: any = {};
    if (hemisphere) params.hemisphere = hemisphere;
    if (season) params.season = season;
    return this.http.get<any>('/culture/seasonal', { params });
  }

  getTropicalCalendar(): Observable<any> {
    return this.http.get<any>('/culture/tropical-calendar');
  }

  compare(fruitA: string, fruitB: string): Observable<any> {
    return this.http.get<any>('/culture/compare', { params: { fruit_a: fruitA, fruit_b: fruitB } });
  }
}
