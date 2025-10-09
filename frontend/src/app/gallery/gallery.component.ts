import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-gallery',
  templateUrl: './gallery.component.html',
  styleUrls: ['./gallery.component.scss'],
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, MatTooltipModule, RouterModule]
})
export class GalleryComponent implements OnInit {
  classes: string[] = [];
  samples: { [key: string]: string[] } = {};
  loading = false;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loading = true;
    this.http.get<any>('/vision/classes').subscribe({
      next: (res) => {
        this.classes = res.classes || [];
        this.classes.forEach(c => this.loadSamples(c));
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  loadSamples(cls: string) {
    this.http.get<any>(`/vision/samples?cls=${encodeURIComponent(cls)}&n=6`).subscribe({
      next: res => { this.samples[cls] = res.samples || [] },
      error: () => { this.samples[cls] = [] }
    });
  }

  imgUrl(cls: string, file: string) {
    return `/vision/image?cls=${encodeURIComponent(cls)}&file=${encodeURIComponent(file)}`;
  }
}
