import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-fruit-culture',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, MatIconModule],
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
        <div class="hero-icon">
          <mat-icon>spa</mat-icon>
        </div>
        <h1 class="gradient-text">Fruit Culture Encyclopedia</h1>
        <p class="hero-subtitle">Global cultivation, trade, and sustainability data for every fruit</p>
        <div class="hero-stats" *ngIf="globalStats">
          <div class="stat-item" *ngFor="let s of entries(globalStats).slice(0,6)">
            <div class="stat-value">{{ s[1] | number }}</div>
            <div class="stat-label">{{ fmt(s[0]) }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="page-section">
      <div class="search-bar">
        <input type="text" [(ngModel)]="query" placeholder="Search fruit culture..." class="premium-input" (input)="filter()">
      </div>

      <div class="culture-grid">
        <div class="premium-card culture-card" *ngFor="let fruit of filteredCultures" (click)="selectFruit(fruit.name)">
          <h3>{{ fruit.name }}</h3>
          <p class="origin">{{ fruit.origin }}</p>
          <p class="regions">{{ fruit.regions?.slice(0,3).join(', ') }}</p>
          <div class="culture-footer">
            <span>{{ fruit.production | number }}t/yr</span>
            <span>{{ fruit.varieties }} varieties</span>
          </div>
        </div>
      </div>

      <div class="modal-overlay" *ngIf="detail" (click)="detail=null">
        <div class="premium-card modal-content" (click)="$event.stopPropagation()">
          <button class="modal-close" (click)="detail=null">&times;</button>
          <h2>{{ detail.fruit | titlecase }}</h2>
          <div class="modal-grid">
            <div class="modal-section">
              <h4>Cultivation</h4>
              <div *ngFor="let item of entries(detail.cultivation)" class="info-row">
                <span class="info-key">{{ fmt(item[0]) }}</span>
                <span class="info-val">{{ item[1] }}</span>
              </div>
            </div>
            <div class="modal-section">
              <h4>Trade</h4>
              <div *ngFor="let item of entries(detail.trade)" class="info-row">
                <span class="info-key">{{ fmt(item[0]) }}</span>
                <span class="info-val">{{ item[1] | number }}</span>
              </div>
            </div>
            <div class="modal-section">
              <h4>Sustainability</h4>
              <div *ngFor="let item of entries(detail.sustainability)" class="info-row">
                <span class="info-key">{{ fmt(item[0]) }}</span>
                <span class="info-val">{{ item[1] }}</span>
              </div>
            </div>
            <div class="modal-section full">
              <h4>Varieties ({{ detail.varieties?.length }})</h4>
              <div class="chip-group">
                <span class="chip" *ngFor="let v of detail.varieties">{{ v }}</span>
              </div>
              <h4 style="margin-top:16px">Fun Facts</h4>
              <ul><li *ngFor="let f of detail.fun_facts">{{ f }}</li></ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .culture-card h3 { margin: 0 0 4px; }
    .origin { font-size: .85rem; color: var(--text-muted); margin: 8px 0; }
    .regions { font-size: .8rem; color: var(--primary); }
    .culture-footer { display: flex; justify-content: space-between; font-size: .75rem; color: var(--text-muted); margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--border-color); }
    .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.7); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
    .modal-content { max-width: 800px; width: 100%; max-height: 85vh; overflow-y: auto; position: relative; }
    .modal-close { position: absolute; top: 12px; right: 16px; background: none; border: none; color: var(--text-muted); font-size: 1.8rem; cursor: pointer; line-height: 1; }
    .modal-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 16px; }
    .modal-section.full { grid-column: 1 / -1; }
    .info-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,.04); font-size: .82rem; }
    .info-key { color: var(--text-muted); }
    .info-val { color: var(--text-primary); font-weight: 500; text-align: right; }
    .search-bar { margin-bottom: 24px; }
    .premium-input { width: 100%; box-sizing: border-box; }
    .culture-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(280px,1fr)); gap: 18px; }
    .culture-card { cursor: pointer; }
    .culture-card:hover { transform: translateY(-3px); border-color: var(--primary); box-shadow: 0 8px 30px rgba(0,0,0,.3); }
    @media (max-width:768px) { .modal-grid { grid-template-columns: 1fr; } }
  `]
})
export class FruitCultureComponent implements OnInit {
  globalStats: any = {};
  cultures: any[] = [];
  filteredCultures: any[] = [];
  detail: any = null;
  query = '';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.http.get<any>('/api/culture/global-stats').subscribe(r => this.globalStats = r);
    this.http.get<any>('/api/culture/fruits').subscribe(r => {
      this.cultures = Object.entries(r.cultures || {}).map(([k,v]:any) => ({
        name: k, origin: v.origin, regions: v.primary_regions,
        production: v.global_production_tonnes, varieties: v.variety_count
      }));
      this.filteredCultures = [...this.cultures];
    });
  }

  selectFruit(name: string) {
    this.http.get<any>(`/api/culture/fruit/${name}`).subscribe(r => this.detail = r);
  }

  filter() {
    const q = this.query.toLowerCase();
    this.filteredCultures = this.cultures.filter(c => c.name.includes(q) || c.origin?.toLowerCase().includes(q));
  }

  entries(obj: any): [string,any][] { return Object.entries(obj || {}); }
  fmt(k: string): string { return k.replace(/_/g,' '); }
}
