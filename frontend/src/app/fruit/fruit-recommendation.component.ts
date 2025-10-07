import { Component } from '@angular/core';
import { FruitopiaApiService } from './fruitopia-api.service';

@Component({
  selector: 'app-fruit-recommendation',
  template: `<div>
    <mat-form-field appearance="fill">
      <mat-label>Disease or Symptom</mat-label>
      <input matInput [(ngModel)]="disease" placeholder="e.g. diabetes">
    </mat-form-field>
    <button mat-raised-button color="primary" (click)="getRecommendations()">Get Recommendations</button>
    <div *ngIf="recommended.length">
      <h3>Recommended Fruits:</h3>
      <mat-list>
        <mat-list-item *ngFor="let fruit of recommended">{{ fruit.name }}</mat-list-item>
      </mat-list>
    </div>
  </div>`,
  styleUrls: []
})
export class FruitRecommendationComponent {
  disease: string = '';
  recommended: any[] = [];
  constructor(private api: FruitopiaApiService) {}

  getRecommendations() {
    this.api.getRecommendations(this.disease).subscribe((res: any) => {
      this.recommended = res.recommended || [];
    });
  }
}
