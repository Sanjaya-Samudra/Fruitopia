import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class BarcodeService {
  constructor(private http: HttpClient) {}

  lookup(barcode: string): Observable<any> {
    return this.http.post<any>('/barcode/lookup', { barcode });
  }

  getHistory(limit?: number): Observable<any> {
    return this.http.get<any>('/barcode/history', { params: limit ? { limit } : {} });
  }

  searchByCountry(country: string): Observable<any> {
    return this.http.get<any>('/barcode/search/country', { params: { country } });
  }
}

@Injectable({ providedIn: 'root' })
export class PremiumService {
  constructor(private http: HttpClient) {}

  getTiers(): Observable<any> {
    return this.http.get<any>('/premium/tiers');
  }

  subscribe(userId: string, tier: string, billingCycle?: string): Observable<any> {
    return this.http.post<any>('/premium/subscribe', { user_id: userId, tier, billing_cycle: billingCycle });
  }

  cancel(userId: string): Observable<any> {
    return this.http.post<any>('/premium/cancel', { user_id: userId });
  }

  upgrade(userId: string, tier: string): Observable<any> {
    return this.http.post<any>('/premium/upgrade', { user_id: userId, tier });
  }

  getSubscription(userId: string): Observable<any> {
    return this.http.get<any>('/premium/subscription', { params: { user_id: userId } });
  }
}
