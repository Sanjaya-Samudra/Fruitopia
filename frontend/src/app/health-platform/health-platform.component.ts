import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HealthPlatformService } from '../services/health-platform.service';

@Component({
  selector: 'app-health-platform',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page">
      <div class="page-header">
        <h1>Health Platform Integration</h1>
        <p>Connect wearables to get personalized fruit recommendations</p>
      </div>

      <div class="platform-grid">
        <div class="platform-card" *ngFor="let p of platforms">
          <h3>{{ p.name }}</h3>
          <p class="data-types">Data: {{ p.data_types?.join(', ') }}</p>
          <button class="btn-primary" (click)="connect(p.id)" [disabled]="connected[p.id]">
            {{ connected[p.id] ? 'Connected' : 'Connect' }}
          </button>
          <span class="connected-badge" *ngIf="connected[p.id]">Connected</span>
        </div>
      </div>

      <div class="metrics-section" *ngIf="hasMetrics()">
        <h3>Current Health Metrics</h3>
        <div class="metrics-grid">
          <div class="metric" *ngFor="let m of getEntries(metrics)">
            <span class="metric-val">{{ m[1] }}</span>
            <span class="metric-lbl">{{ fmt(m[0]) }}</span>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .platform-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px,1fr)); gap: 20px; }
    .platform-card { background: var(--surface); border-radius: 14px; padding: 20px; text-align: center; position: relative; }
    .data-types { font-size: .8rem; color: var(--text-muted); margin: 10px 0; }
    .metrics-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px,1fr)); gap: 12px; margin-top: 16px; }
    .metric { background: rgba(255,255,255,.05); border-radius: 10px; padding: 14px; text-align: center; }
    .metric-val { display: block; font-size: 1.2rem; font-weight: 700; color: var(--primary); }
    .metric-lbl { font-size: .65rem; text-transform: uppercase; color: var(--text-muted); }
    .connected-badge { position: absolute; top: 12px; right: 12px; background: var(--primary); color: #fff; font-size: .6rem; padding: 2px 8px; border-radius: 10px; }
  `]
})
export class HealthPlatformComponent implements OnInit {
  platforms: any[] = [];
  connected: any = {};
  metrics: any = {};

  constructor(private service: HealthPlatformService) {}

  fmt(k: string): string { return k.replace(/_/g, ' '); }

  getEntries(obj: any): [string, any][] { return Object.entries(obj || {}); }

  hasMetrics(): boolean { return Object.keys(this.metrics).length > 0; }

  ngOnInit() {
    this.service.listPlatforms().subscribe(r => this.platforms = r.platforms);
  }

  connect(id: string) {
    this.service.connect(id, 'athlete').subscribe(r => {
      if (r.status === 'connected') {
        this.connected[id] = true;
        this.service.getMetrics(id).subscribe(m => this.metrics = m);
      }
    });
  }
}
