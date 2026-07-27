import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-barcode-scanner',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, MatIconModule],
  template: `
    <div class="page-container">
      <div class="page-title">
        <h1><span class="gradient-text">Barcode Scanner</span></h1>
        <p class="subtitle">Look up fruit information by barcode</p>
      </div>

      <div class="scanner-card">
        <div class="scan-row">
          <input type="text" [(ngModel)]="barcode" placeholder="Enter barcode (e.g. 040100000101)" class="scan-input" maxlength="14">
          <button class="btn-primary" (click)="lookup()" [disabled]="!barcode.trim()">Look Up</button>
        </div>
      </div>

      <div *ngIf="error" class="error-banner">{{ error }}</div>

      <div *ngIf="result" class="result-card">
        <div *ngIf="result.found" class="result-found">
          <h2>{{ result.fruit | titlecase }}</h2>
          <div class="result-grid">
            <div class="result-item"><span class="r-key">Variety</span><span class="r-val">{{ result.variety }}</span></div>
            <div class="result-item"><span class="r-key">Brand</span><span class="r-val">{{ result.brand }}</span></div>
            <div class="result-item"><span class="r-key">Country of Origin</span><span class="r-val">{{ result.country_of_origin }}</span></div>
            <div class="result-item"><span class="r-key">Barcode</span><span class="r-val">{{ result.barcode }}</span></div>
          </div>
          <button class="btn-primary" style="margin-top:16px" [routerLink]="['/explore', result.fruit]">View Fruit Details</button>
        </div>
        <div *ngIf="!result.found" class="result-not-found">
          <mat-icon>search_off</mat-icon>
          <p>{{ result.message || 'Fruit not found in database.' }}</p>
        </div>
      </div>

      <div class="country-section">
        <h3>Search by Country of Origin</h3>
        <div class="scan-row">
          <input type="text" [(ngModel)]="country" placeholder="Enter country name..." class="scan-input">
          <button class="btn-primary" (click)="searchCountry()">Search</button>
        </div>
        <div *ngIf="countryResults?.length" class="country-results">
          <div class="country-chip" *ngFor="let r of countryResults">
            {{ r.variety }} {{ r.fruit }} <span class="country-tag">{{ r.country }}</span>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .scanner-card, .country-section { background: var(--surface); border-radius: 20px; padding: 28px; border: 1px solid var(--border-color); margin-bottom: 20px; }
    .scan-row { display: flex; gap: 12px; }
    .scan-input { flex:1; padding: 14px 20px; border-radius: 12px; border: 1px solid var(--border-color); background: rgba(255,255,255,.05); color: var(--text-primary); font-size: 1rem; letter-spacing: 2px; }
    .result-card { background: var(--surface); border-radius: 20px; padding: 28px; border: 1px solid var(--border-color); margin-bottom: 20px; }
    .result-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px; }
    .result-item { display: flex; flex-direction: column; gap: 2px; }
    .r-key { font-size: .72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; }
    .r-val { font-size: .95rem; font-weight: 600; }
    .result-not-found { text-align: center; padding: 40px 20px; color: var(--text-muted); }
    .result-not-found mat-icon { font-size: 48px; width: 48px; height: 48px; margin-bottom: 12px; opacity: .5; }
    .country-results { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
    .country-chip { padding: 8px 16px; border-radius: 20px; background: rgba(255,255,255,.06); border: 1px solid var(--border-color); font-size: .82rem; }
    .country-tag { color: var(--primary); font-weight: 600; margin-left: 6px; }
    @media (max-width:768px) { .result-grid { grid-template-columns: 1fr; } }
  `]
})
export class BarcodeScannerComponent {
  barcode = '';
  country = '';
  result: any = null;
  countryResults: any[] = [];
  error = '';

  constructor(private http: HttpClient) {}

  lookup() {
    if (!this.barcode.trim()) return;
    this.error = '';
    this.http.post<any>('/barcode/lookup', { barcode: this.barcode.trim() }).subscribe({
      next: r => this.result = r,
      error: () => this.error = 'Failed to look up barcode. Ensure backend is running.'
    });
  }

  searchCountry() {
    if (!this.country.trim()) return;
    this.http.get<any>('/barcode/search/country', { params: { country: this.country } }).subscribe(r => this.countryResults = r.results || []);
  }
}
