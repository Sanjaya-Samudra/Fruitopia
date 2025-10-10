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
    // Backend expects the file field to be named 'file'
    fd.append('file', image, image.name);
    return this.http.post('/vision/predict', fd);
  }
}
