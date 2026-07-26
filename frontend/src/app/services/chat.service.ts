import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';

export interface ChatMessage {
  role: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

@Injectable({ providedIn: 'root' })
export class ChatService {
  private chatOpenSubject = new BehaviorSubject<boolean>(false);
  public chatOpen$ = this.chatOpenSubject.asObservable();
  public messages: ChatMessage[] = [];
  private sessionId: string | null = null;

  constructor(private http: HttpClient) {}

  toggleChat(): void {
    this.chatOpenSubject.next(!this.chatOpenSubject.value);
    if (this.chatOpenSubject.value && this.messages.length === 0) {
      this.messages.push({
        role: 'bot',
        content: "Hi! I'm your Fruitopia AI nutrition assistant. I can help with fruit recommendations, nutrition info, recipes, and health advice. What would you like to know?",
        timestamp: new Date()
      });
    }
  }

  openChat(): void {
    this.chatOpenSubject.next(true);
  }

  closeChat(): void {
    this.chatOpenSubject.next(false);
  }

  get isChatOpen(): boolean {
    return this.chatOpenSubject.value;
  }

  sendMessage(message: string): Observable<{ response: string; session_id: string }> {
    this.messages.push({ role: 'user', content: message, timestamp: new Date() });
    return this.http.post<{ response: string; session_id: string }>('/chatbot/message', {
      message,
      session_id: this.sessionId
    });
  }

  setSessionId(id: string) {
    this.sessionId = id;
  }
}
