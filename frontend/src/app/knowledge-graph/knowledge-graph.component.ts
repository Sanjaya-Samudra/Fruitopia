import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-knowledge-graph',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page-container">
      <div class="page-title">
        <h1><span class="gradient-text">Evidence Research Graph</span></h1>
        <p class="subtitle">PubMed-cited research connecting fruits, nutrients, and health outcomes</p>
      </div>

      <div *ngIf="stats" class="stat-bar">
        <div class="stat-card" *ngFor="let s of entries(stats)">
          <div class="stat-val">{{ s[1] }}</div>
          <div class="stat-lbl">{{ fmt(s[0]) }}</div>
        </div>
      </div>

      <div class="search-bar">
        <input type="text" [(ngModel)]="query" placeholder="Search fruits, diseases, or nutrients..." class="search-input">
        <button class="btn-primary" (click)="search()">Search</button>
      </div>

      <div *ngIf="searchResult" class="search-results">
        <div *ngIf="searchResult.fruits?.length" class="result-group">
          <h4>Fruits</h4>
          <div class="chip-row"><span class="chip" *ngFor="let f of searchResult.fruits" (click)="loadFruit(f.name)">{{ f.name }}</span></div>
        </div>
        <div *ngIf="searchResult.evidence?.length" class="result-group">
          <h4>Evidence ({{ searchResult.evidence.length }})</h4>
          <div class="evidence-list">
            <div class="evidence-card" *ngFor="let e of searchResult.evidence">
              <strong>{{ e.title }}</strong>
              <p class="ev-conf">Confidence: {{ (e.confidence * 100).toFixed(0) }}%</p>
            </div>
          </div>
        </div>
      </div>

      <div *ngIf="fruitData" class="fruit-evidence">
        <h2>{{ currentFruit | titlecase }}</h2>
        <div *ngIf="fruitData.relationships?.direct_relationships?.length" class="relationships">
          <h4>Relationships</h4>
          <div class="chip-row">
            <span class="chip" *ngFor="let r of fruitData.relationships.direct_relationships.slice(0,10)">{{ r.target }} ({{ r.type | lowercase }})</span>
          </div>
        </div>
        <div class="evidence-grid" *ngIf="fruitData.evidence?.length">
          <div class="evidence-card" *ngFor="let e of fruitData.evidence">
            <h4>{{ e.title }}</h4>
            <p class="ev-journal">{{ e.journal }} ({{ e.year }})</p>
            <p class="ev-summary">{{ e.summary }}</p>
            <div class="ev-meta">
              <span>Effect: <strong>{{ e.effect_size }}</strong></span>
              <span>Confidence: <strong>{{ (e.confidence * 100).toFixed(0) }}%</strong></span>
              <a *ngIf="e.doi" [href]="'https://doi.org/'+e.doi" target="_blank" class="doi-link">View Study</a>
            </div>
          </div>
        </div>
        <div *ngIf="!fruitData.evidence?.length" class="empty-state">
          <p>No evidence entries found for this fruit.</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .stat-bar { display: grid; grid-template-columns: repeat(auto-fit,minmax(140px,1fr)); gap: 12px; margin-bottom: 28px; }
    .stat-card { background: var(--surface); border-radius: 14px; padding: 18px; text-align: center; border: 1px solid var(--border-color); }
    .stat-val { font-size: 1.3rem; font-weight: 700; color: var(--primary); }
    .stat-lbl { font-size: .65rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; margin-top: 4px; }
    .search-bar { display: flex; gap: 12px; margin-bottom: 24px; }
    .search-input { flex:1; padding: 14px 20px; border-radius: 12px; border: 1px solid var(--border-color); background: var(--surface); color: var(--text-primary); font-size: .95rem; }
    .chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0; }
    .chip { padding: 6px 16px; border-radius: 20px; background: rgba(255,255,255,.06); border: 1px solid var(--border-color); cursor: pointer; font-size: .82rem; transition: all .2s; }
    .chip:hover { border-color: var(--primary); }
    .evidence-grid, .evidence-list { display: grid; grid-template-columns: repeat(auto-fill,minmax(340px,1fr)); gap: 16px; }
    .evidence-card { background: var(--surface); border-radius: 14px; padding: 20px; border: 1px solid var(--border-color); border-left: 3px solid var(--primary); }
    .evidence-card h4 { font-size: .9rem; margin-bottom: 6px; line-height: 1.3; }
    .ev-journal { font-size: .78rem; color: var(--text-muted); font-style: italic; }
    .ev-summary { font-size: .82rem; line-height: 1.5; margin: 10px 0; }
    .ev-meta { display: flex; flex-wrap: wrap; gap: 12px; font-size: .78rem; align-items: center; }
    .ev-meta span { color: var(--text-muted); }
    .doi-link { color: var(--primary); text-decoration: none; font-weight: 600; margin-left: auto; }
    .fruit-evidence h2 { margin: 28px 0 16px; }
    .relationships { margin-bottom: 20px; }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--text-muted); }
  `]
})
export class KnowledgeGraphComponent implements OnInit {
  stats: any = {};
  query = '';
  searchResult: any = null;
  fruitData: any = null;
  currentFruit = '';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.http.get<any>('/api/knowledge-graph/stats').subscribe(r => this.stats = r);
  }

  search() {
    if (!this.query.trim()) return;
    this.http.get<any>('/api/knowledge-graph/search', { params: { q: this.query } }).subscribe(r => {
      this.searchResult = r;
      this.fruitData = null;
    });
  }

  loadFruit(name: string) {
    this.currentFruit = name;
    this.http.get<any>(`/api/knowledge-graph/fruit/${name}`).subscribe(r => this.fruitData = r);
  }

  entries(obj: any): [string,any][] { return Object.entries(obj || {}); }
  fmt(k: string): string { return k.replace(/_/g,' '); }
}
