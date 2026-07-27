import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-health-platform',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page-container">
      <div class="page-title">
        <h1><span class="gradient-text">Health Platform Integration</span></h1>
        <p class="subtitle">Connect your wearables for personalized fruit recommendations</p>
      </div>

      <div class="platform-grid">
        <div class="platform-card" *ngFor="let p of platforms">
          <div class="platform-header">
            <h3>{{ p.name }}</h3>
            <span class="platform-badge" *ngIf="connected[p.id]" (click)="disconnect(p.id)">Connected</span>
          </div>
          <p class="platform-data">Data: {{ p.data_types?.join(', ') }}</p>
          <div class="platform-profiles" *ngIf="!connected[p.id]">
            <label>Profile:</label>
            <select [(ngModel)]="selectedProfile" class="profile-select">
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
        <h3>Latest Health Metrics</h3>
        <div class="metrics-grid">
          <div class="metric-card" *ngFor="let m of entries(metrics)">
            <div class="metric-val">{{ m[1] }}</div>
            <div class="metric-lbl">{{ fmt(m[0]) }}</div>
          </div>
        </div>
      </div>

      <div *ngIf="recs?.length" class="recs-section">
        <h3>Personalized Fruit Recommendations</h3>
        <div class="recs-grid">
          <div class="rec-chip" *ngFor="let r of recs">{{ r.fruit }} ({{ r.match_score }}%)</div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .platform-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(280px,1fr)); gap: 18px; }
    .platform-card { background: var(--surface); border-radius: 18px; padding: 24px; border: 1px solid var(--border-color); }
    .platform-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .platform-header h3 { font-size: 1.05rem; }
    .platform-badge { font-size: .7rem; background: var(--primary); color: #fff; padding: 3px 10px; border-radius: 10px; cursor: pointer; }
    .platform-data { font-size: .8rem; color: var(--text-muted); margin-bottom: 14px; line-height: 1.4; }
    .platform-profiles { margin-bottom: 14px; }
    .platform-profiles label { font-size: .78rem; color: var(--text-muted); display: block; margin-bottom: 6px; }
    .profile-select { width: 100%; padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border-color); background: rgba(255,255,255,.05); color: var(--text-primary); }
    .metrics-section, .recs-section { margin-top: 32px; }
    .metrics-section h3, .recs-section h3 { margin-bottom: 16px; }
    .metrics-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(110px,1fr)); gap: 10px; }
    .metric-card { background: var(--surface); border-radius: 12px; padding: 16px; text-align: center; border: 1px solid var(--border-color); }
    .metric-val { font-size: 1.1rem; font-weight: 700; color: var(--primary); }
    .metric-lbl { font-size: .62rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; margin-top: 4px; }
    .recs-grid { display: flex; flex-wrap: wrap; gap: 8px; }
    .rec-chip { padding: 8px 18px; border-radius: 20px; background: rgba(255,255,255,.06); border: 1px solid var(--border-color); font-size: .85rem; }
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
    this.http.get<any>('/health/platforms').subscribe(r => this.platforms = r.platforms || []);
  }

  connect(id: string) {
    this.http.post<any>('/health/platforms/connect', { platform_id: id, profile_type: this.selectedProfile }).subscribe({
      next: r => {
        if (r.status === 'connected') {
          this.connected[id] = true;
          this.http.get<any>('/health/metrics', { params: { platform_id: id } }).subscribe(m => this.metrics = m);
          this.http.post<any>('/health/recommendations', { platform_id: id }).subscribe(r2 => this.recs = r2.recommendations || []);
        }
      }
    });
  }

  disconnect(id: string) {
    this.http.post<any>('/health/platforms/disconnect', { platform_id: id }).subscribe(() => delete this.connected[id]);
  }

  entries(obj: any): [string,any][] { return Object.entries(obj || {}); }
  fmt(k: string): string { return k.replace(/_/g,' '); }
}
