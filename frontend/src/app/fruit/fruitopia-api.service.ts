import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class FruitopiaApiService {
  private baseUrl = 'http://localhost:8000'; // Adjust if backend runs elsewhere

  constructor(private http: HttpClient) {}

  getFruits(category?: string): Observable<any> {
    let url = `${this.baseUrl}/fruits`;
    if (category && category !== 'all') {
      url += `?category=${category}`;
    }
    return this.http.get(url);
  }

  getFruitDetail(name: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/fruits/${name}`);
  }

  getRecommendations(disease: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/recommend`, { disease });
  }

  nlpExtract(text: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/nlp/extract`, { text });
  }

  identifyFruit(image: File): Observable<any> {
    const formData = new FormData();
    formData.append('image', image);
    return this.http.post(`${this.baseUrl}/vision/identify`, formData);
  }

  chatbotMessage(message: string, sessionId?: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/chatbot/message`, { message, session_id: sessionId });
  }
}
