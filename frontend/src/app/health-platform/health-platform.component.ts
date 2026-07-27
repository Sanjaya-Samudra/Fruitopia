import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-health-platform',
  standalone: true,
  imports: [CommonModule, FormsModule, MatIconModule],
  template: `
    <div class="page-hero">
      <div class="hero-bg">
        <div class="glass-overlay"></div>
        <div class="floating-shapes">
          <div class="shape s1"></div>
          <div class="shape s2"></div>
          <div class="shape s3"></div>
        </div>
      </div>
      <div class="hero-content">
        <div class="hero-icon"><mat-icon>monitor_heart</mat-icon></div>
        <h1><span class="gradient-text">Health Platform Integration</span></h1>
        <p class="hero-subtitle">Connect your wearables for personalized fruit recommendations</p>
        <div class="hero-stats" *ngIf="platforms.length">
          <div class="stat-item">
            <span class="stat-value">{{ platforms.length }}</span>
            <span class="stat-label">Platforms</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ entries(connected).length }}</span>
            <span class="stat-label">Connected</span>
          </div>
        </div>
      </div>
    </div>

    <div class="page-section">
      <div class="platform-grid">
        <div class="premium-card" *ngFor="let p of platforms">
          <div class="platform-header">
            <h3>{{ p.name }}</h3>
            <span class="chip active" *ngIf="connected[p.id]" (click)="disconnect(p.id)">Connected</span>
          </div>
          <p class="platform-data">Data: {{ p.data_types?.join(', ') }}</p>
          <div class="platform-profiles" *ngIf="!connected[p.id]">
            <label>Profile:</label>
            <select [(ngModel)]="selectedProfile" class="premium-select">
              <option value="athlete">Athlete</option>
              <option value="office_worker">Office Worker</option>
              <option value="senior">Senior</option>
            </select>
          </div>
          <button class="btn-primary" (click)="connect(p.id)" [disabled]="connected[p.id]">
            {{ connected[p.id] ? 'Connected' : 'Connect & Sync' }}
          </button>
        </div>
      </div>

      <div *ngIf="metrics && entries(metrics).length" class="metrics-section">
        <h3 style="margin-bottom:16px">Latest Health Metrics</h3>
        <div class="metrics-grid">
          <div class="premium-card metric-card" *ngFor="let m of entries(metrics)">
            <div class="metric-val">{{ m[1] }}</div>
            <div class="metric-lbl">{{ fmt(m[0]) }}</div>
          </div>
        </div>
      </div>

      <div *ngIf="recs?.length" class="recs-section">
        <h3 style="margin-bottom:16px">Personalized Fruit Recommendations</h3>
        <div class="chip-group">
          <span class="chip" *ngFor="let r of recs">{{ r.fruit }} ({{ r.match_score }}%)</span>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .platform-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(280px,1fr)); gap: 18px; margin-bottom: 32px; }
    .platform-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .platform-header h3 { font-size: 1.05rem; margin: 0; }
    .platform-data { font-size: .82rem; color: var(--text-muted); margin-bottom: 14px; line-height: 1.4; }
    .platform-profiles { margin-bottom: 14px; }
    .platform-profiles label { font-size: .78rem; color: var(--text-muted); display: block; margin-bottom: 6px; }
    .metrics-section, .recs-section { margin-top: 32px; }
    .metrics-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(110px,1fr)); gap: 10px; }
    .metric-card { text-align: center; }
    .metric-val { font-size: 1.1rem; font-weight: 700; color: var(--primary); }
    .metric-lbl { font-size: .62rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; margin-top: 4px; }
  `]
})
export class HealthPlatformComponent implements OnInit {
  platforms: any[] = [];
  connected: any = {};
  metrics: any = {};
  recs: any[] = [];
  selectedProfile = 'office_worker';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.http.get<any>('/api/health/platforms').subscribe(r => this.platforms = r.platforms || []);
  }

  connect(id: string) {
    this.http.post<any>('/api/health/platforms/connect', { platform_id: id, profile_type: this.selectedProfile }).subscribe({
      next: r => {
        if (r.status === 'connected') {
          this.connected[id] = true;
          this.http.get<any>('/api/health/metrics', { params: { platform_id: id } }).subscribe(m => this.metrics = m);
          this.http.post<any>('/api/health/recommendations', { platform_id: id }).subscribe(r2 => this.recs = r2.recommendations || []);
        }
      }
    });
  }

  disconnect(id: string) {
    this.http.post<any>('/api/health/platforms/disconnect', { platform_id: id }).subscribe(() => delete this.connected[id]);
  }

  entries(obj: any): [string,any][] { return Object.entries(obj || {}); }
  fmt(k: string): string { return k.replace(/_/g,' '); }
}
