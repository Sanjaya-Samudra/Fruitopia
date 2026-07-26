import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class HealthPlatformService {
  constructor(private http: HttpClient) {}

  listPlatforms(): Observable<any> {
    return this.http.get<any>('/health/platforms');
  }

  connect(platformId: string, profileType?: string): Observable<any> {
    return this.http.post<any>('/health/platforms/connect', { platform_id: platformId, profile_type: profileType });
  }

  disconnect(platformId: string): Observable<any> {
    return this.http.post<any>('/health/platforms/disconnect', { platform_id: platformId });
  }

  getMetrics(platformId?: string): Observable<any> {
    return this.http.get<any>('/health/metrics', { params: platformId ? { platform_id: platformId } : {} });
  }

  getRecommendations(platformId: string): Observable<any> {
    return this.http.post<any>('/health/recommendations', { platform_id: platformId });
  }

  getSyncStatus(): Observable<any> {
    return this.http.get<any>('/health/sync-status');
  }
}
