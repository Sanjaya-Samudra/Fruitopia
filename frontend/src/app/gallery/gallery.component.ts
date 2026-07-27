import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-gallery',
  templateUrl: './gallery.component.html',
  styleUrls: ['./gallery.component.scss'],
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, MatTooltipModule, MatProgressSpinnerModule, RouterModule]
})
export class GalleryComponent implements OnInit {
  classes: string[] = [];
  samples: { [key: string]: string[] } = {};
  loading = false;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loading = true;
    this.http.get<any>('/api/vision/classes').subscribe({
      next: (res) => {
        this.classes = res.classes || [];
        this.classes.forEach(c => this.loadSamples(c));
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  loadSamples(cls: string) {
    this.http.get<any>(`/api/vision/samples?cls=${encodeURIComponent(cls)}&n=6`).subscribe({
      next: res => { this.samples[cls] = res.samples || [] },
      error: () => { this.samples[cls] = [] }
    });
  }

  imgUrl(cls: string, file: string) {
    return `/api/vision/image?cls=${encodeURIComponent(cls)}&file=${encodeURIComponent(file)}`;
  }

  getFruitIcon(cls: string): string {
    const icons: { [key: string]: string } = {
      'apple': '🍎',
      'apples': '🍎',
      'banana': '🍌',
      'bananas': '🍌',
      'orange': '🍊',
      'oranges': '🍊',
      'strawberry': '🍓',
      'strawberries': '🍓',
      'blueberry': '🫐',
      'blueberries': '🫐',
      'mango': '🥭',
      'mangos': '🥭',
      'pineapple': '🍍',
      'pineapples': '🍍',
      'kiwi': '🥝',
      'kiwifruit': '🥝',
      'grape': '🍇',
      'grapes': '🍇',
      'watermelon': '🍉',
      'watermelons': '🍉',
      'peach': '🍑',
      'peaches': '🍑',
      'pear': '🍐',
      'pears': '🍐',
      'cherry': '🍒',
      'cherries': '🍒',
      'lemon': '🍋',
      'lemons': '🍋',
      'lime': '🍋',
      'limes': '🍋',
      'avocado': '🥑',
      'avocados': '🥑',
      'coconut': '🥥',
      'coconuts': '🥥',
      'fig': '🫠',
      'figs': '🫠'
    };
    return icons[cls.toLowerCase()] || '🍽️';
  }

  trackByClass(index: number, cls: string): string {
    return cls;
  }
}
