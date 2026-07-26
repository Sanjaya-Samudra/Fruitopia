import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PremiumService } from '../services/barcode.service';

interface TierInfo { name: string; price_monthly: number; price_yearly: number; features: Record<string, boolean>; }

@Component({
  selector: 'app-premium',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="page">
      <div class="page-header">
        <h1>Premium Plans</h1>
        <p>Unlock the full power of the Fruitopia platform</p>
      </div>
      <div class="tier-grid">
        <div class="tier-card" *ngFor="let t of getTierEntries()">
          <h2>{{ t.name }}</h2>
          <div class="price"><span class="amount">\${{ t.price_monthly }}</span><span class="period">/month</span></div>
          <p class="yearly">\${{ t.price_yearly }}/year</p>
          <ul class="features">
            <li *ngFor="let item of getFeatureList(t.features)" [class.inc]="item[1]" [class.missing]="!item[1]">
              <span class="feature-icon">{{ item[1] ? '+' : '-' }}</span>
              <span class="feature-name">{{ item[0] }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .tier-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px,1fr)); gap: 24px; }
    .tier-card { background: var(--surface); border-radius: 20px; padding: 28px 20px; text-align: center; border: 1px solid var(--border); transition: transform .2s; }
    .tier-card:hover { transform: translateY(-4px); border-color: var(--primary); }
    .price { margin: 16px 0; }
    .amount { font-size: 2.5rem; font-weight: 800; color: var(--primary); }
    .period { font-size: .9rem; color: var(--text-muted); }
    .yearly { font-size: .8rem; color: var(--text-muted); margin-bottom: 20px; }
    .features { list-style: none; padding: 0; text-align: left; }
    .features li { padding: 6px 0; font-size: .8rem; border-bottom: 1px solid rgba(255,255,255,.05); display: flex; gap: 8px; align-items: center; }
    .feature-icon { width: 16px; text-align: center; font-weight: 700; }
    .inc .feature-icon { color: var(--primary); }
    .missing .feature-icon { color: var(--text-muted); }
    .inc { color: var(--text); }
    .missing { color: var(--text-muted); opacity: .5; }
  `]
})
export class PremiumComponent implements OnInit {
  tiers: Record<string, TierInfo> = {};

  constructor(private service: PremiumService) {}

  ngOnInit() { this.service.getTiers().subscribe(r => this.tiers = r.tiers); }

  getTierEntries(): TierInfo[] { return Object.values(this.tiers); }

  getFeatureList(features: any): [string, boolean][] {
    if (!features) return [];
    return Object.entries(features).map(([k, v]) => [k.replace(/_/g, ' '), v as boolean]);
  }
}
