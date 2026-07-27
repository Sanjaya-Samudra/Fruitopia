import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-premium',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule],
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
        <div class="hero-icon"><mat-icon>workspace_premium</mat-icon></div>
        <h1><span class="gradient-text">Premium Plans</span></h1>
        <p class="hero-subtitle">Unlock the full power of the Fruitopia platform</p>
        <div class="hero-stats" *ngIf="tiers.length">
          <div class="stat-item">
            <span class="stat-value">{{ tiers.length }}</span>
            <span class="stat-label">Plans Available</span>
          </div>
        </div>
      </div>
    </div>

    <div class="page-section">
      <div class="tier-grid">
        <div class="premium-card" *ngFor="let t of tiers" [class.popular]="t.name === 'Pro'" style="text-align:center">
          <span class="chip active" *ngIf="t.name === 'Pro'" style="margin-bottom:16px;display:inline-block">Most Popular</span>
          <h2>{{ t.name }}</h2>
          <div class="tier-price">
            <span class="price-amount">\${{ t.price_monthly }}</span>
            <span class="price-period">/month</span>
          </div>
          <p class="price-yearly">\${{ t.price_yearly }}/year</p>
          <ul class="feature-list">
            <li *ngFor="let f of getFeatures(t.features)" [class.included]="f[1]" [class.excluded]="!f[1]">
              <span class="feature-check">{{ f[1] ? '✓' : '—' }}</span>
              {{ f[0] }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .tier-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(260px,1fr)); gap: 22px; }
    .premium-card.popular { border-color: var(--primary); box-shadow: 0 0 30px rgba(129,140,248,.15); }
    .tier-price { margin: 16px 0; }
    .price-amount { font-size: 2.8rem; font-weight: 800; background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .price-period { font-size: .9rem; color: var(--text-muted); }
    .price-yearly { font-size: .8rem; color: var(--text-muted); margin-bottom: 24px; }
    .feature-list { list-style: none; padding: 0; text-align: left; }
    .feature-list li { padding: 8px 0; font-size: .82rem; border-bottom: 1px solid rgba(255,255,255,.04); display: flex; align-items: center; gap: 10px; }
    .feature-check { width: 20px; text-align: center; }
    .included { color: var(--text-primary); }
    .included .feature-check { color: var(--primary); font-weight: 700; }
    .excluded { color: var(--text-muted); opacity: .5; }
  `]
})
export class PremiumComponent implements OnInit {
  tiers: any[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.http.get<any>('/api/premium/tiers').subscribe(r => {
      this.tiers = Object.entries(r.tiers || {}).map(([k,v]: any) => ({ id: k, ...v }));
    });
  }

  getFeatures(features: any): [string, boolean][] {
    return Object.entries(features || {}).map(([k,v]) => [k.replace(/_/g,' '), v as boolean]);
  }
}
