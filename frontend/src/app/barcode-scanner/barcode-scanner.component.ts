import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BarcodeService } from '../services/barcode.service';

@Component({
  selector: 'app-barcode-scanner',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page">
      <div class="page-header">
        <h1>Barcode Scanner</h1>
        <p>Look up fruit information by barcode</p>
      </div>

      <div class="scanner-section">
        <input type="text" [(ngModel)]="barcode" placeholder="Enter barcode (e.g. 040100000101)" class="scan-input" maxlength="14">
        <button class="btn-primary" (click)="lookup()" [disabled]="!barcode">Look Up</button>
      </div>

      <div class="result" *ngIf="result">
        <div class="found" *ngIf="result.found">
          <h2>{{ result.fruit | titlecase }}</h2>
          <div class="info-grid">
            <div><strong>Variety:</strong> {{ result.variety }}</div>
            <div><strong>Brand:</strong> {{ result.brand }}</div>
            <div><strong>Country:</strong> {{ result.country_of_origin }}</div>
            <div><strong>Barcode:</strong> {{ result.barcode }}</div>
          </div>
        </div>
        <div class="not-found" *ngIf="!result.found">
          <p>{{ result.message }}</p>
        </div>
      </div>

      <div class="country-search">
        <h3>Search by Country</h3>
        <input type="text" [(ngModel)]="country" placeholder="Country name..." class="scan-input">
        <button class="btn-primary" (click)="searchCountry()">Search</button>
        <div class="country-results" *ngIf="countryResults?.length">
          <div class="barcode-chip" *ngFor="let r of countryResults">{{ r.variety }} {{ r.fruit }} ({{ r.country }})</div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .scanner-section, .country-search { background: var(--surface); border-radius: 16px; padding: 24px; margin-bottom: 24px; display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
    .scan-input { flex: 1; min-width: 200px; padding: 12px 16px; border-radius: 10px; border: 1px solid var(--border); background: rgba(255,255,255,.05); color: var(--text); font-size: 1rem; letter-spacing: 2px; }
    .result { background: var(--surface); border-radius: 14px; padding: 24px; margin-bottom: 24px; }
    .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px; }
    .not-found { color: var(--text-muted); }
    .country-results { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; width: 100%; }
    .barcode-chip { background: rgba(255,255,255,.05); border: 1px solid var(--border); border-radius: 20px; padding: 6px 14px; font-size: .8rem; }
    @media (max-width:768px) { .info-grid { grid-template-columns: 1fr; } }
  `]
})
export class BarcodeScannerComponent {
  barcode = '';
  country = '';
  result: any = null;
  countryResults: any[] = [];

  constructor(private service: BarcodeService) {}

  lookup() {
    if (!this.barcode) return;
    this.service.lookup(this.barcode).subscribe(r => this.result = r);
  }

  searchCountry() {
    if (!this.country) return;
    this.service.searchByCountry(this.country).subscribe(r => this.countryResults = r.results);
  }
}
