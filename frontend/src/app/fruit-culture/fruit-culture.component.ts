import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-fruit-culture',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="page-container">
      <div class="page-title">
        <h1><span class="gradient-text">Fruit Culture Encyclopedia</span></h1>
        <p class="subtitle">Global cultivation, trade, and sustainability data for every fruit</p>
      </div>

      <div *ngIf="globalStats" class="stat-bar">
        <div class="stat-card" *ngFor="let s of entries(globalStats).slice(0,6)">
          <div class="stat-val">{{ s[1] | number }}</div>
          <div class="stat-lbl">{{ fmt(s[0]) }}</div>
        </div>
      </div>

      <div class="search-bar">
        <input type="text" [(ngModel)]="query" placeholder="Search fruit culture..." class="search-input" (input)="filter()">
      </div>

      <div class="culture-grid">
        <div class="culture-card" *ngFor="let fruit of filteredCultures" (click)="selectFruit(fruit.name)">
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
        <div class="modal-content" (click)="$event.stopPropagation()">
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
              <div class="variety-chips">
                <span class="variety-chip" *ngFor="let v of detail.varieties">{{ v }}</span>
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
    .stat-bar { display: grid; grid-template-columns: repeat(auto-fit,minmax(150px,1fr)); gap: 12px; margin-bottom: 28px; }
    .stat-card { background: var(--surface); border-radius: 14px; padding: 18px 14px; text-align: center; border: 1px solid var(--border-color); }
    .stat-val { font-size: 1.2rem; font-weight: 700; color: var(--primary); }
    .stat-lbl { font-size: .65rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; margin-top: 4px; }
    .search-bar { margin-bottom: 24px; }
    .search-input { width: 100%; padding: 14px 20px; border-radius: 12px; border: 1px solid var(--border-color); background: var(--surface); color: var(--text-primary); font-size: .95rem; box-sizing: border-box; }
    .culture-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(280px,1fr)); gap: 18px; }
    .culture-card { background: var(--surface); border-radius: 16px; padding: 24px; border: 1px solid var(--border-color); cursor: pointer; transition: all .25s; }
    .culture-card:hover { transform: translateY(-3px); border-color: var(--primary); box-shadow: 0 8px 30px rgba(0,0,0,.3); }
    .origin { font-size: .85rem; color: var(--text-muted); margin: 8px 0; }
    .regions { font-size: .8rem; color: var(--primary); }
    .culture-footer { display: flex; justify-content: space-between; font-size: .75rem; color: var(--text-muted); margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--border-color); }
    .modal-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .modal-section.full { grid-column: 1 / -1; }
    .info-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,.04); font-size: .82rem; }
    .info-key { color: var(--text-muted); }
    .info-val { color: var(--text-primary); font-weight: 500; text-align: right; }
    .variety-chips { display: flex; flex-wrap: wrap; gap: 6px; }
    .variety-chip { padding: 4px 12px; border-radius: 20px; background: rgba(255,255,255,.06); font-size: .78rem; }
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
    this.http.get<any>('/culture/global-stats').subscribe(r => this.globalStats = r);
    this.http.get<any>('/culture/fruits').subscribe(r => {
      this.cultures = Object.entries(r.cultures || {}).map(([k,v]:any) => ({
        name: k, origin: v.origin, regions: v.primary_regions,
        production: v.global_production_tonnes, varieties: v.variety_count
      }));
      this.filteredCultures = [...this.cultures];
    });
  }

  selectFruit(name: string) {
    this.http.get<any>(`/culture/fruit/${name}`).subscribe(r => this.detail = r);
  }

  filter() {
    const q = this.query.toLowerCase();
    this.filteredCultures = this.cultures.filter(c => c.name.includes(q) || c.origin?.toLowerCase().includes(q));
  }

  entries(obj: any): [string,any][] { return Object.entries(obj || {}); }
  fmt(k: string): string { return k.replace(/_/g,' '); }
}
