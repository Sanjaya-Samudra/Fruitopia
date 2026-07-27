import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-premium',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="page-container">
      <div class="page-title">
        <h1><span class="gradient-text">Premium Plans</span></h1>
        <p class="subtitle">Unlock the full power of the Fruitopia platform</p>
      </div>

      <div class="tier-grid">
        <div class="tier-card" *ngFor="let t of tiers" [class.popular]="t.name === 'Pro'">
          <div class="tier-badge" *ngIf="t.name === 'Pro'">Most Popular</div>
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
    .tier-card { background: var(--surface); border-radius: 22px; padding: 32px 24px; border: 1px solid var(--border-color); text-align: center; position: relative; transition: all .25s; }
    .tier-card:hover { transform: translateY(-4px); }
    .tier-card.popular { border-color: var(--primary); box-shadow: 0 0 30px rgba(129,140,248,.15); }
    .tier-badge { position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: var(--gradient-primary); color: #fff; font-size: .7rem; font-weight: 700; padding: 4px 18px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px; }
    .tier-card h2 { font-size: 1.2rem; margin-bottom: 16px; }
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
