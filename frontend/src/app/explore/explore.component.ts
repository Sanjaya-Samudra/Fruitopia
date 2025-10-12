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
import { LeafletModule } from '@asymmetrik/ngx-leaflet';
import { latLng, tileLayer, marker, icon, MapOptions } from 'leaflet';
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
    MatButtonModule,
    LeafletModule
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
  public activeTab: 'overview' | 'nutrition' | 'culinary' | 'science' | 'cultivation' | 'facts' = 'overview';
  public vitamins: Array<[string, any]> = [];
  public datasetSamples: string[] = [];
  public gallery: string[] = []; // combined images from JSON + dataset
  public donutGradient: string | null = null;
  public minerals: Array<[string, any]> = [];
  public macroPercentages: {carbs:number,protein:number,fat:number} = {carbs:0,protein:0,fat:0};
  public svgArcs: Array<{color:string,start:number,end:number,label:string}> = [];
  public lightboxOpen = false;
  public lightboxIndex = 0;
  public expandedDescription = false;

  // Map properties
  public mapOptions: MapOptions = {};
  public mapLayers: any[] = [];
  public mapCenter: [number, number] = [0, 0];
  public showMap = false;

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
  // expose first gallery image (if any) for hero
  public get heroImage(): string | null {
    return (this.gallery && this.gallery.length) ? this.gallery[0] : null;
  }

  // description expand/collapse
  public toggleDescription(expand?: boolean) {
    if (typeof expand === 'boolean') this.expandedDescription = expand;
    else this.expandedDescription = !this.expandedDescription;
  }

  // format vitamin/mineral names for display
  private formatNutrientName(key: string): string {
    const nutrientMap: { [key: string]: string } = {
      // Vitamins
      'vitaminA_IU_or_µg': 'Vitamin A',
      'vitaminB1_mg': 'Vitamin B1',
      'vitaminB2_mg': 'Vitamin B2', 
      'vitaminB3_mg': 'Vitamin B3',
      'vitaminB5_mg': 'Vitamin B5',
      'vitaminB6_mg': 'Vitamin B6',
      'folate_µg': 'Folate',
      'vitaminC_mg': 'Vitamin C',
      'vitaminD_IU': 'Vitamin D',
      'vitaminE_mg': 'Vitamin E',
      'vitaminK_µg': 'Vitamin K',
      
      // Minerals
      'calcium_mg': 'Calcium',
      'iron_mg': 'Iron',
      'magnesium_mg': 'Magnesium',
      'phosphorus_mg': 'Phosphorus',
      'potassium_mg': 'Potassium',
      'zinc_mg': 'Zinc',
      'sodium_mg': 'Sodium'
    };
    
    return nutrientMap[key] || key;
  }

  // format nutrient value with unit
  private formatNutrientValue(key: string, value: any): string {
    const unitMap: { [key: string]: string } = {
      // Vitamins
      'vitaminA_IU_or_µg': 'µg',
      'vitaminB1_mg': 'mg',
      'vitaminB2_mg': 'mg',
      'vitaminB3_mg': 'mg',
      'vitaminB5_mg': 'mg',
      'vitaminB6_mg': 'mg',
      'folate_µg': 'µg',
      'vitaminC_mg': 'mg',
      'vitaminD_IU': 'IU',
      'vitaminE_mg': 'mg',
      'vitaminK_µg': 'µg',
      
      // Minerals
      'calcium_mg': 'mg',
      'iron_mg': 'mg',
      'magnesium_mg': 'mg',
      'phosphorus_mg': 'mg',
      'potassium_mg': 'mg',
      'zinc_mg': 'mg',
      'sodium_mg': 'mg'
    };
    
    const unit = unitMap[key] || '';
    return `${value}${unit ? ' ' + unit : ''}`;
  }

  public formatJson(value: any): string {
    if (typeof value === 'string') {
      return value;
    }
    return JSON.stringify(value, null, 2);
  }

  constructor(private readonly route: ActivatedRoute, private readonly http: HttpClient) {}
  ngOnInit(): void {
    // keyboard nav for lightbox
    window.addEventListener('keydown', (e: KeyboardEvent) => {
      if (!this.lightboxOpen) return;
      if (e.key === 'ArrowRight') this.nextLightbox();
      if (e.key === 'ArrowLeft') this.prevLightbox();
      if (e.key === 'Escape') this.closeLightbox();
    });
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
              
              // Process vitamins and minerals
              const vitaminsData = this.fruit?.nutritionalFacts?.vitamins || {};
              const mineralsData = this.fruit?.nutritionalFacts?.minerals || {};
              
              this.vitamins = Object.entries(vitaminsData)
                .map(([key, value]) => [this.formatNutrientName(key), this.formatNutrientValue(key, value)]);
              this.minerals = Object.entries(mineralsData)
                .map(([key, value]) => [this.formatNutrientName(key), this.formatNutrientValue(key, value)]);
              
              // Initialize map if geolocation data exists
              this.initializeMap();
            } catch (e) {
              console.error('Error processing nutrition data:', e);
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

  private initializeMap(): void {
    if (!this.fruit?.geolocationAndMapping?.GISCoordinates || this.fruit.geolocationAndMapping.GISCoordinates.length < 1) {
      this.showMap = false;
      return;
    }

    // Parse the first coordinate string (format: "lat, lng")
    const coordString = this.fruit.geolocationAndMapping.GISCoordinates[0];
    const [latStr, lngStr] = coordString.split(',').map((s: string) => s.trim());
    const lat = parseFloat(latStr);
    const lng = parseFloat(lngStr);

    if (isNaN(lat) || isNaN(lng)) {
      this.showMap = false;
      return;
    }

    this.mapCenter = [lat, lng];
    this.showMap = true;

    this.mapOptions = {
      layers: [
        tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 18,
          attribution: '© OpenStreetMap contributors'
        })
      ],
      zoom: 8,
      center: latLng(lat, lng)
    };

    this.mapLayers = [
      marker([lat, lng], {
        icon: icon({
          iconSize: [25, 41],
          iconAnchor: [13, 41],
          iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
          shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png'
        })
      }).bindPopup(`<b>${this.fruit.fruitName}</b><br>Origin: ${this.fruit.origin}`)
    ];
  }

  public showTab(tab: 'overview' | 'nutrition' | 'culinary' | 'science' | 'cultivation' | 'facts') {
    this.activeTab = tab;
  }

  // Normalize pairings data to always return an array
  public getNormalizedPairings(): string[] {
    const pairings = this.fruit?.culinaryInformation?.pairings;
    if (Array.isArray(pairings)) {
      return pairings;
    } else if (typeof pairings === 'string') {
      // Split string by commas and clean up
      return pairings.split(',').map(p => p.trim()).filter(p => p.length > 0);
    }
    return [];
  }

  // Normalize propagation methods to always return an array
  public getNormalizedPropagationMethods(): string[] {
    const methods = this.fruit?.cultivation?.propagationMethods;
    if (Array.isArray(methods)) {
      return methods;
    } else if (typeof methods === 'string') {
      // Split string by commas and clean up
      return methods.split(',').map(m => m.trim()).filter(m => m.length > 0);
    }
    return [];
  }
}
