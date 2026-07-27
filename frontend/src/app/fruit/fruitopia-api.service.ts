import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class FruitopiaApiService {
  constructor(private http: HttpClient) {}

  getFruits(category?: string): Observable<any> {
    let url = `/api/fruits`;
    if (category && category !== 'all') {
      url += `?category=${category}`;
    }
    return this.http.get(url);
  }

  getFruitDetail(name: string): Observable<any> {
    return this.http.get(`/api/fruits/${name}`);
  }

  getRecommendations(disease: string): Observable<any> {
    return this.http.post(`/api/recommend`, { disease });
  }

  nlpExtract(text: string): Observable<any> {
    return this.http.post(`/api/nlp/extract`, { text });
  }

  identifyFruit(image: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', image, image.name);
    return this.http.post(`/api/vision/predict`, formData);
  }

  chatbotMessage(message: string, sessionId?: string): Observable<any> {
    return this.http.post(`/api/chatbot/message`, { message, session_id: sessionId });
  }

  generateRecipe(requestData: any): Observable<any> {
    return this.http.post(`/api/recipes/generate`, requestData);
  }
}
