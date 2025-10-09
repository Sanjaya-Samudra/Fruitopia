import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RecommendService } from '../services/recommend.service';
import { HttpClientModule } from '@angular/common/http';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-recommend',
  templateUrl: './recommend.component.html',
  styleUrls: ['./recommend.component.scss'],
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule, MatButtonModule, MatFormFieldModule, MatInputModule, MatSelectModule, MatCardModule]
})
export class RecommendComponent implements OnInit {
  diseases: string[] = [];
  disease = '';
  typedDisease = '';
  have: string[] = [];
  availableClasses: string[] = [];
  recommendations: any[] = [];
  loading = false;

  constructor(private svc: RecommendService) {}

  ngOnInit(): void {
    this.svc.listDiseases().subscribe({ next: (res) => {
      console.debug('recommend: received diseases', res);
      this.diseases = res.diseases || []
    }, error: (err) => {
      console.error('recommend: failed to list diseases', err);
      this.diseases = [];
    } });
    // fetch classes for checkbox list (simple xhr to vision/classes)
    fetch('/vision/classes').then(r => r.json()).then(j => this.availableClasses = j.classes || []);
  }

  getRecommendations() {
    this.loading = true;
    const diseaseToUse = (this.typedDisease && this.typedDisease.trim()) ? this.typedDisease.trim() : this.disease;
    this.svc.recommend(diseaseToUse, this.have).subscribe({ next: (res) => {
      this.recommendations = res.recommendations || [];
      this.loading = false;
    }, error: () => { this.loading = false } });
  }

  imageUrl(cls: string, sample?: string) {
    if (!sample) return '';
    return '/vision/image?cls=' + encodeURIComponent(cls) + '&file=' + encodeURIComponent(sample);
  }
}
