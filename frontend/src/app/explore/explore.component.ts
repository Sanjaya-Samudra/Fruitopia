import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { HttpClientModule } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatButtonModule } from '@angular/material/button';
import { catchError } from 'rxjs/operators';
import { of } from 'rxjs';

@Component({
  selector: 'app-explore',
  standalone: true,
  imports: [
    CommonModule,
    HttpClientModule,
    MatCardModule,
    MatChipsModule,
    MatIconModule,
    MatProgressBarModule,
    MatExpansionModule,
    MatButtonModule
  ],
  schemas: [CUSTOM_ELEMENTS_SCHEMA], // Added to suppress unknown element errors
  templateUrl: './explore.component.html',
  styleUrls: ['./explore.component.scss']
})
export class ExploreComponent implements OnInit {
  public name: string | null = null;
  public fruit: any = null;
  public loading = true;
  public error: string | null = null;
  public vitamins: Array<[string, any]> = [];
  public datasetSamples: string[] = [];
  public gallery: string[] = []; // combined images from JSON + dataset
  public donutGradient: string | null = null;
  public minerals: Array<[string, any]> = [];
  public macroPercentages: {carbs:number,protein:number,fat:number} = {carbs:0,protein:0,fat:0};
  public svgArcs: Array<{color:string,start:number,end:number,label:string}> = [];
  public lightboxOpen = false;
  public lightboxIndex = 0;

  // convert degrees to cartesian coordinate on circle
  private polarToCartesian(cx: number, cy: number, radius: number, angleInDegrees: number) {
    const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
    return {
      x: cx + (radius * Math.cos(angleInRadians)),
      y: cy + (radius * Math.sin(angleInRadians))
    };
  }

  // describe a donut arc path between start and end degrees
  public describeArc(cx: number, cy: number, radius: number, startAngle: number, endAngle: number) {
    const start = this.polarToCartesian(cx, cy, radius, endAngle);
    const end = this.polarToCartesian(cx, cy, radius, startAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';
    const d = [
      'M', start.x, start.y,
      'A', radius, radius, 0, largeArcFlag, 0, end.x, end.y
    ].join(' ');
    return d;
  }

  // lightbox controls
  public openLightbox(index: number) {
    this.lightboxIndex = index;
    this.lightboxOpen = true;
  }
  public closeLightbox() { this.lightboxOpen = false; }
  public nextLightbox() { this.lightboxIndex = (this.lightboxIndex + 1) % (this.gallery.length || 1); }
  public prevLightbox() { this.lightboxIndex = (this.lightboxIndex - 1 + (this.gallery.length || 1)) % (this.gallery.length || 1); }
  public formatJson(value: any): string {
    if (typeof value === 'string') {
      return value;
    }
    return JSON.stringify(value, null, 2);
  }

  constructor(private readonly route: ActivatedRoute, private readonly http: HttpClient) {}
  ngOnInit(): void {
    this.name = this.route.snapshot.paramMap.get('name');
    if (!this.name) {
      this.error = 'No fruit specified';
      this.loading = false;
      return;
    }

    const key = this.name.toLowerCase();
    // Try same-origin SPA route first so the Angular app serves the page and
    // the component can fetch JSON via XHR; fall back to direct backend URL
    // and static fallbacks if needed.
    const candidates = [
      `/explore/${key}`,
      `http://127.0.0.1:8000/explore/${key}`,
      `/backend/data/explore/${key}.json`,
      `/data/explore/${key}.json`,
      `/assets/explore/${key}.json`
    ];

    const tryNext = (idx: number) => {
      if (idx >= candidates.length) {
        this.error = `Could not load data for ${key}`;
        this.loading = false;
        return;
      }
      const url = candidates[idx];
      this.http.get(url).pipe(catchError(() => of(null))).subscribe(res => {
        if (res) {
          this.fruit = res;
            // after we have the fruit JSON, fetch dataset sample filenames and build gallery
          const jsonImgs = (this.fruit?.appearance?.images || []).filter((i: string) => !!i);
          this.http.get(`/vision/samples?cls=${encodeURIComponent(key)}&n=6`).pipe(catchError(() => of({samples:[]}))).subscribe((resp: any) => {
            const samples = resp && resp.samples ? resp.samples : [];
            const datasetUrls = samples.map((f: string) => `/vision/image?cls=${encodeURIComponent(key)}&file=${encodeURIComponent(f)}`);
            this.datasetSamples = samples;
            // Only use dataset images, not JSON images
            this.gallery = [...datasetUrls];
            // prepare nutrition visuals
            try {
              const macros = (this.fruit?.nutritionalFacts?.macronutrients) || {};
              const carbs = Number(macros.carbohydrates_g) || 0;
              const protein = Number(macros.protein_g) || 0;
              const fat = Number(macros.fat_g) || 0;
              const total = (carbs + protein + fat) || 1;
              const pc1 = Math.round((carbs / total) * 100);
              const pc2 = Math.round((protein / total) * 100);
              const pc3 = 100 - pc1 - pc2;
              this.donutGradient = `conic-gradient(#2b9df4 0% ${pc1}%, #7bd389 ${pc1}% ${pc1 + pc2}%, #f4a261 ${pc1 + pc2}% 100%)`;
              this.macroPercentages = {carbs: pc1, protein: pc2, fat: pc3};
              // build simple SVG arc descriptors (degrees)
              let start = 0;
              this.svgArcs = [];
              const colors = ['#2b9df4','#7bd389','#f4a261'];
              const labels = ['Carbs','Protein','Fat'];
              const pcts = [pc1, pc2, pc3];
              for (let i=0;i<3;i++){
                const end = start + (pcts[i] / 100) * 360;
                this.svgArcs.push({color: colors[i], start, end, label: `${labels[i]} ${pcts[i]}%`});
                start = end;
              }
              this.vitamins = Object.entries(this.fruit?.nutritionalFacts?.vitamins || {});
              this.minerals = Object.entries(this.fruit?.nutritionalFacts?.minerals || {});
            } catch (e) {
              this.donutGradient = null;
              this.vitamins = [];
              this.minerals = [];
            }
            this.loading = false;
          }, () => {
            // on error, fall back to JSON images only
            this.gallery = jsonImgs;
            this.loading = false;
          });
        } else {
          tryNext(idx + 1);
        }
      }, () => tryNext(idx + 1));
    };

    tryNext(0);
  }
}
