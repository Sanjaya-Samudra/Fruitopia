import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-fruit-list',
  standalone: true,
  imports: [CommonModule, RouterModule, MatCardModule, MatButtonModule, MatIconModule],
  templateUrl: './fruit-list.component.html',
  styleUrls: ['./fruit-list.component.scss']
})
export class FruitListComponent implements OnInit {
  fruits: any[] = [];
  loading = true;
  error = '';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.http.get<any>('/api/fruits').subscribe({
      next: (data) => {
        this.fruits = data.fruits || data || [];
        this.loading = false;
      },
      error: () => {
        this.error = 'Failed to load fruits';
        this.loading = false;
      }
    });
  }

  imgUrl(cls: string) {
    return `/api/vision/image?cls=${encodeURIComponent(cls)}&file=0.jpg`;
  }

  getFruitIcon(name: string): string {
    const icons: { [key: string]: string } = {
      'apple': '🍎', 'banana': '🍌', 'orange': '🍊',
      'strawberry': '🍓', 'blueberry': '🫐', 'mango': '🥭',
      'pineapple': '🍍', 'kiwi': '🥝', 'grape': '🍇',
      'watermelon': '🍉', 'peach': '🍑', 'pear': '🍐',
      'cherry': '🍒', 'lemon': '🍋', 'lime': '🍋',
      'avocado': '🥑', 'coconut': '🥥', 'fig': '🫠',
      'pomegranate': '🍎', 'apricot': '🍑', 'plum': '🍑',
      'raspberry': '🍓', 'blackberry': '🍓', 'guava': '🍈',
      'passionfruit': '🍈', 'tomato': '🍅', 'cantaloupe': '🍈',
      'grapefruit': '🍊', 'olive': '🫒', 'acerola': '🍒'
    };
    return icons[name.toLowerCase()] || '🍏';
  }
}
