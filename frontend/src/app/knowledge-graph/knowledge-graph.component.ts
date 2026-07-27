import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-knowledge-graph',
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
        <div class="hero-icon">
          <mat-icon>hub</mat-icon>
        </div>
        <h1 class="gradient-text">Evidence Research Graph</h1>
        <p class="hero-subtitle">PubMed-cited research connecting fruits, nutrients, and health outcomes</p>
        <div class="hero-stats" *ngIf="stats">
          <div class="stat-item" *ngFor="let s of entries(stats)">
            <div class="stat-value">{{ s[1] }}</div>
            <div class="stat-label">{{ fmt(s[0]) }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="page-section">
      <div class="search-bar">
        <input type="text" [(ngModel)]="query" placeholder="Search fruits, diseases, or nutrients..." class="premium-input">
        <button class="btn-primary" (click)="search()">Search</button>
      </div>

      <div *ngIf="searchResult" class="search-results">
        <div *ngIf="searchResult.fruits?.length" class="result-group">
          <h4>Fruits</h4>
          <div class="chip-group">
            <span class="chip" *ngFor="let f of searchResult.fruits" (click)="loadFruit(f.name)">{{ f.name }}</span>
          </div>
        </div>
        <div *ngIf="searchResult.evidence?.length" class="result-group">
          <h4>Evidence ({{ searchResult.evidence.length }})</h4>
          <div class="evidence-list">
            <div class="premium-card" *ngFor="let e of searchResult.evidence">
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
          <div class="chip-group">
            <span class="chip" *ngFor="let r of fruitData.relationships.direct_relationships.slice(0,10)">{{ r.target }} ({{ r.type | lowercase }})</span>
          </div>
        </div>
        <div class="evidence-grid" *ngIf="fruitData.evidence?.length">
          <div class="premium-card" *ngFor="let e of fruitData.evidence">
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
    .search-bar { display: flex; gap: 12px; margin-bottom: 24px; }
    .premium-input { flex: 1; }
    .result-group { margin-bottom: 20px; }
    .result-group h4 { margin-bottom: 10px; }
    .evidence-list, .evidence-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(340px,1fr)); gap: 16px; }
    .evidence-list .premium-card, .evidence-grid .premium-card { border-left: 3px solid var(--primary); }
    .premium-card h4 { font-size: .9rem; margin-bottom: 6px; line-height: 1.3; }
    .ev-conf { font-size: .82rem; color: var(--text-muted); margin-top: 6px; }
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
