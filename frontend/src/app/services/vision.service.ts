import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Prediction {
  class: string;
  score: number;
}

@Injectable({ providedIn: 'root' })
export class VisionService {
  private base = '/vision';
  constructor(private http: HttpClient) {}

  predict(image: File): Observable<any> {
    const fd = new FormData();
    fd.append('image', image, image.name);
    return this.http.post('/vision/predict', fd);
  }
}
