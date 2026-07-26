import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FruitCultureService } from '../services/fruit-culture.service';

@Component({
  selector: 'app-fruit-culture',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page">
      <div class="page-header">
        <h1>Fruit Culture Encyclopedia</h1>
        <p>Global fruit cultivation, trade, and sustainability data</p>
      </div>

      <div class="stats-bar">
        <div class="stat" *ngFor="let s of getEntries(globalStats)">
          <span class="stat-val">{{ s[1] | number }}</span>
          <span class="stat-lbl">{{ fmt(s[0]) }}</span>
        </div>
      </div>

      <div class="search-section">
        <input type="text" [(ngModel)]="searchQuery" placeholder="Search fruit culture..." class="search-input">
        <button class="btn-primary" (click)="search()">Search</button>
      </div>

      <div class="culture-grid">
        <div class="culture-card" *ngFor="let c of getCulturesList()" (click)="selectFruit(c.name)">
          <h3>{{ c.name | titlecase }}</h3>
          <p class="origin">{{ c.origin }}</p>
          <p class="regions">{{ c.regions?.join(', ') }}</p>
          <div class="culture-meta">
            <span>Production: {{ c.production | number }}t</span>
            <span>{{ c.varieties }} varieties</span>
          </div>
        </div>
      </div>

      <div class="modal" *ngIf="selectedFruit" (click)="selectedFruit = null">
        <div class="modal-content" (click)="$event.stopPropagation()">
          <button class="modal-close" (click)="selectedFruit = null">&times;</button>
          <h2>{{ selectedFruit | titlecase }}</h2>
          <div class="detail-grid">
            <div class="detail-section">
              <h4>Cultivation</h4>
              <div *ngFor="let item of getEntries(detail?.cultivation)">
                <strong>{{ fmt(item[0]) }}:</strong> {{ item[1] }}
              </div>
            </div>
            <div class="detail-section">
              <h4>Trade</h4>
              <div *ngFor="let item of getEntries(detail?.trade)">
                <strong>{{ fmt(item[0]) }}:</strong> {{ item[1] }}
              </div>
            </div>
            <div class="detail-section">
              <h4>Sustainability</h4>
              <div *ngFor="let item of getEntries(detail?.sustainability)">
                <strong>{{ fmt(item[0]) }}:</strong> {{ item[1] }}
              </div>
            </div>
            <div class="detail-section">
              <h4>Varieties</h4>
              <p>{{ detail?.varieties?.join(', ') }}</p>
              <h4>Fun Facts</h4>
              <ul><li *ngFor="let f of detail?.fun_facts">{{ f }}</li></ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .stats-bar { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px,1fr)); gap: 16px; margin-bottom: 28px; }
    .stat { background: var(--surface); border-radius: 12px; padding: 16px; text-align: center; }
    .stat-val { display: block; font-size: 1.3rem; font-weight: 700; color: var(--primary); }
    .stat-lbl { font-size: .7rem; text-transform: uppercase; color: var(--text-muted); }
    .search-section { display: flex; gap: 12px; margin-bottom: 24px; }
    .search-input { flex:1; padding: 12px 16px; border-radius: 10px; border: 1px solid var(--border); background: var(--surface); color: var(--text); font-size: .95rem; }
    .culture-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px,1fr)); gap: 20px; }
    .culture-card { background: var(--surface); border-radius: 14px; padding: 20px; cursor: pointer; transition: transform .2s, box-shadow .2s; }
    .culture-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,.3); }
    .origin { font-size: .85rem; color: var(--text-muted); margin: 6px 0; }
    .culture-meta { display: flex; justify-content: space-between; font-size: .75rem; color: var(--primary); margin-top: 10px; }
    .detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .detail-section h4 { color: var(--primary); margin: 12px 0 6px; font-size: .9rem; }
    .detail-section div { font-size: .8rem; margin: 4px 0; }
    @media (max-width:768px) { .detail-grid { grid-template-columns: 1fr; } }
  `]
})
export class FruitCultureComponent implements OnInit {
  cultures: any = {};
  globalStats: any = {};
  selectedFruit: string | null = null;
  detail: any = null;
  searchQuery = '';

  constructor(private service: FruitCultureService) {}

  fmt(k: string): string { return k.replace(/_/g, ' '); }

  getEntries(obj: any): [string, any][] { return Object.entries(obj || {}); }

  getCulturesList(): any[] {
    return Object.entries(this.cultures).map(([name, data]: any) => ({
      name,
      origin: data.origin,
      regions: data.primary_regions,
      production: data.global_production_tonnes,
      varieties: data.variety_count,
    }));
  }

  ngOnInit() {
    this.service.getCultures().subscribe(r => this.cultures = r.cultures);
    this.service.getGlobalStats().subscribe(r => this.globalStats = r);
  }

  selectFruit(name: string) {
    this.selectedFruit = name;
    this.service.getFruitDetail(name).subscribe(r => this.detail = r);
  }

  search() {
    if (!this.searchQuery.trim()) return;
    this.service.getCultures().subscribe(r => {
      const q = this.searchQuery.toLowerCase();
      this.cultures = Object.entries(r.cultures)
        .filter(([k]) => k.includes(q))
        .reduce((a: any, [k, v]: any) => (a[k] = v, a), {});
    });
  }
}
