import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { KnowledgeGraphService } from '../services/knowledge-graph.service';

@Component({
  selector: 'app-knowledge-graph',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page">
      <div class="page-header">
        <h1>Evidence Knowledge Graph</h1>
        <p>PubMed-cited research connecting fruits, nutrients, and health</p>
      </div>

      <div class="stats-row">
        <div class="stat-box" *ngFor="let s of getEntries(stats)"><span class="num">{{ s[1] }}</span><span class="desc">{{ formatKey(s[0]) }}</span></div>
      </div>

      <div class="search-section">
        <input type="text" [(ngModel)]="query" placeholder="Search fruits, diseases, nutrients..." class="search-input">
        <button class="btn-primary" (click)="doSearch()">Search</button>
      </div>

      <div class="result-section" *ngIf="searchResult">
        <div *ngIf="searchResult.fruits?.length" class="result-group">
          <h3>Fruits</h3>
          <div class="result-chips"><span class="chip" *ngFor="let f of searchResult.fruits" (click)="loadFruit(f.name)">{{ f.name }}</span></div>
        </div>
        <div *ngIf="searchResult.evidence?.length" class="result-group">
          <h3>Evidence ({{ searchResult.evidence.length }})</h3>
          <div class="ev-card" *ngFor="let e of searchResult.evidence">
            <strong>{{ e.title }}</strong>
            <p class="ev-conf">Confidence: {{ e.confidence | percent }}</p>
          </div>
        </div>
      </div>

      <div class="fruit-evidence" *ngIf="fruitEvidence">
        <h3>{{ currentFruit }} - Evidence & Relationships</h3>
        <div class="ev-grid">
          <div class="ev-card" *ngFor="let e of fruitEvidence.evidence">
            <h4>{{ e.title }}</h4>
            <p class="ev-journal">{{ e.journal }} ({{ e.year }})</p>
            <p class="ev-summary">{{ e.summary }}</p>
            <div class="ev-meta">
              <span>Effect: {{ e.effect_size }}</span>
              <span>Confidence: {{ e.confidence | percent }}</span>
              <a *ngIf="e.doi" [href]="'https://doi.org/'+e.doi" target="_blank">DOI</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .stats-row { display: grid; grid-template-columns: repeat(auto-fit,minmax(130px,1fr)); gap: 12px; margin-bottom: 24px; }
    .stat-box { background: var(--surface); border-radius: 10px; padding: 14px; text-align: center; }
    .num { display: block; font-size: 1.3rem; font-weight: 700; color: var(--primary); }
    .desc { font-size: .65rem; text-transform: uppercase; color: var(--text-muted); }
    .search-section { display: flex; gap: 12px; margin-bottom: 24px; }
    .result-chips { display: flex; flex-wrap: wrap; gap: 8px; }
    .chip { background: var(--surface); border: 1px solid var(--primary); border-radius: 20px; padding: 6px 14px; cursor: pointer; font-size: .85rem; }
    .ev-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(320px,1fr)); gap: 16px; }
    .ev-card { background: var(--surface); border-radius: 12px; padding: 18px; border-left: 3px solid var(--primary); }
    .ev-journal { font-size: .8rem; color: var(--text-muted); font-style: italic; }
    .ev-summary { font-size: .85rem; margin: 8px 0; line-height: 1.4; }
    .ev-meta { display: flex; gap: 12px; font-size: .75rem; color: var(--primary); }
    .ev-meta a { color: var(--secondary); text-decoration: none; }
  `]
})
export class KnowledgeGraphComponent implements OnInit {
  stats: any = {};
  query = '';
  searchResult: any = null;
  fruitEvidence: any = null;
  currentFruit = '';

  constructor(private service: KnowledgeGraphService) {}

  ngOnInit() { this.service.getStats().subscribe(r => this.stats = r); }

  formatKey(k: string): string { return k.replace(/_/g, ' '); }

  getEntries(obj: any): [string, any][] { return Object.entries(obj || {}); }

  doSearch() {
    if (!this.query.trim()) return;
    this.service.search(this.query).subscribe(r => {
      this.searchResult = r;
      this.fruitEvidence = null;
    });
  }

  loadFruit(name: string) {
    this.currentFruit = name;
    this.service.getFruitEvidence(name).subscribe(r => this.fruitEvidence = r);
  }
}
