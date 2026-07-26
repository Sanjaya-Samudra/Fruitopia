import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Prediction {
  class: string;
  score: number;
  confidence?: string;
}

export interface PredictResult {
  predictions: Prediction[];
  source: string;
}

@Injectable({ providedIn: 'root' })
export class VisionService {
  constructor(private http: HttpClient) {}

  predict(image: File): Observable<PredictResult> {
    const fd = new FormData();
    fd.append('file', image, image.name);
    return this.http.post<PredictResult>('/vision/predict', fd);
  }

  getClasses(): Observable<{ classes: string[] }> {
    return this.http.get<{ classes: string[] }>('/vision/classes');
  }

  getHealth(): Observable<{ ok: boolean; model_loaded: boolean }> {
    return this.http.get<{ ok: boolean; model_loaded: boolean }>('/vision/health');
  }

  getSamples(cls: string, n: number = 6): Observable<{ samples: string[] }> {
    return this.http.get<{ samples: string[] }>(`/vision/samples?cls=${encodeURIComponent(cls)}&n=${n}`);
  }

  getImageUrl(cls: string, file: string): string {
    return `/vision/image?cls=${encodeURIComponent(cls)}&file=${encodeURIComponent(file)}`;
  }
}
