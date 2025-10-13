import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

export interface Prediction {
  class: string;
  score: number;
}

@Injectable({ providedIn: 'root' })
export class VisionService {
  private base = '/vision';
  constructor(private http: HttpClient) {}

  predict(image: File): Observable<{ predictions: Prediction[]; source?: string }> {
    const fd = new FormData();
    // Backend expects the file field to be named 'file'
    fd.append('file', image, image.name);
    return this.http.post<any>(`${this.base}/predict`, fd).pipe(
      map((res) => this.normalizeResponse(res))
    );
  }

  private normalizeResponse(res: any): { predictions: Prediction[]; source?: string } {
    if (!res) {
      return { predictions: [] };
    }

    if (Array.isArray(res)) {
      return { predictions: this.coerceArray(res), source: undefined };
    }

    if (Array.isArray(res.predictions)) {
      return { predictions: this.coerceArray(res.predictions), source: res.source };
    }

    const single =
      res.fruit ??
      res.class ??
      res.label ??
      res.prediction ??
      res.predicted_label;

    if (single) {
      const score =
        typeof res.score === 'number'
          ? res.score
          : typeof res.confidence === 'number'
          ? res.confidence
          : typeof res.probability === 'number'
          ? res.probability
          : 0.9;

      return { predictions: [{ class: String(single), score }], source: res.source };
    }

    return { predictions: [], source: res.source };
  }

  private coerceArray(items: any[]): Prediction[] {
    return items
      .map((item) => {
        if (typeof item === 'string') {
          return { class: item, score: 0.9 };
        }

        if (Array.isArray(item) && item.length >= 1) {
          const [cls, score] = item;
          return {
            class: String(cls),
            score: typeof score === 'number' ? score : 0.9,
          };
        }

        if (item && typeof item === 'object') {
          const cls = item.class ?? item.label ?? item.fruit ?? item.name;
          const score =
            typeof item.score === 'number'
              ? item.score
              : typeof item.confidence === 'number'
              ? item.confidence
              : typeof item.probability === 'number'
              ? item.probability
              : 0.9;
          if (cls) {
            return { class: String(cls), score };
          }
        }

        return null;
      })
      .filter((p): p is Prediction => Boolean(p));
  }
}
