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
        <div class="hero-icon"><mat-icon>qr_code_scanner</mat-icon></div>
        <h1><span class="gradient-text">Barcode Scanner</span></h1>
        <p class="hero-subtitle">Look up fruit information by barcode</p>
      </div>
    </div>

    <div class="page-section">
      <div class="premium-card">
        <div class="scan-row">
          <input type="text" [(ngModel)]="barcode" placeholder="Enter barcode (e.g. 040100000101)" class="premium-input" maxlength="14">
          <button class="btn-primary" (click)="lookup()" [disabled]="!barcode.trim()">Look Up</button>
        </div>
      </div>

      <div *ngIf="error" class="error-banner">{{ error }}</div>

      <div *ngIf="result" class="premium-card">
        <div *ngIf="result.found">
          <h2 style="margin-bottom:16px">{{ result.fruit | titlecase }}</h2>
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

      <div class="premium-card">
        <h3 style="margin-bottom:16px">Search by Country of Origin</h3>
        <div class="scan-row">
          <input type="text" [(ngModel)]="country" placeholder="Enter country name..." class="premium-input">
          <button class="btn-primary" (click)="searchCountry()">Search</button>
        </div>
        <div *ngIf="countryResults?.length" class="chip-group" style="margin-top:16px">
          <span class="chip" *ngFor="let r of countryResults">
            {{ r.variety }} {{ r.fruit }} <span class="chip active">{{ r.country }}</span>
          </span>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .scan-row { display: flex; gap: 12px; }
    .result-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .result-item { display: flex; flex-direction: column; gap: 2px; }
    .r-key { font-size: .72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; }
    .r-val { font-size: .95rem; font-weight: 600; }
    .result-not-found { text-align: center; padding: 40px 20px; color: var(--text-muted); }
    .result-not-found mat-icon { font-size: 48px; width: 48px; height: 48px; margin-bottom: 12px; opacity: .5; }
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
    this.http.post<any>('/api/barcode/lookup', { barcode: this.barcode.trim() }).subscribe({
      next: r => this.result = r,
      error: () => this.error = 'Failed to look up barcode. Ensure backend is running.'
    });
  }

  searchCountry() {
    if (!this.country.trim()) return;
    this.http.get<any>('/api/barcode/search/country', { params: { country: this.country } }).subscribe(r => this.countryResults = r.results || []);
  }
}
