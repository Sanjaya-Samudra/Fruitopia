import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { RecommendService } from '../services/recommend.service';
import { HttpClientModule } from '@angular/common/http';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-recommend',
  templateUrl: './recommend.component.html',
  styleUrls: ['./recommend.component.scss'],
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, HttpClientModule, MatButtonModule, MatFormFieldModule, MatInputModule, MatSelectModule, MatCardModule, MatIconModule, MatProgressSpinnerModule]
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

  getDiseaseIcon(disease: string): string {
    const icons: { [key: string]: string } = {
      'diabetes': 'bloodtype',
      'anemia': 'opacity',
      'constipation': 'schedule',
      'hypertension': 'monitor_heart',
      'general': 'health_and_safety'
    };
    return icons[disease.toLowerCase()] || 'health_and_safety';
  }

  getFruitIcon(fruit: string): string {
    // Return a placeholder fruit icon URL - you can replace with actual fruit icons
    return `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%230f5140'><circle cx='12' cy='12' r='10'/></svg>`;
  }

  getHealthBadgeClass(fruit: string): string {
    // Simple logic for badge colors - you can customize based on actual health benefits
    const excellent = ['blueberries', 'strawberries', 'apples', 'oranges'];
    const good = ['bananas', 'grapes', 'lemons', 'kiwifruit'];
    const beneficial = ['pineapples', 'mangos', 'peaches', 'pears'];

    if (excellent.includes(fruit.toLowerCase())) return 'excellent';
    if (good.includes(fruit.toLowerCase())) return 'good';
    return 'beneficial';
  }

  getHealthBadgeText(fruit: string): string {
    const badgeClass = this.getHealthBadgeClass(fruit);
    switch (badgeClass) {
      case 'excellent': return 'Excellent';
      case 'good': return 'Good';
      case 'beneficial': return 'Beneficial';
      default: return 'Beneficial';
    }
  }
}
