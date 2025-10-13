import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { FruitopiaApiService } from '../fruit/fruitopia-api.service';
import { ChatService } from '../services/chat.service';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { Subscription } from 'rxjs';

interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  type?: 'text' | 'quick_actions' | 'fruit_card';
  data?: any;
}

interface FruitCard {
  name: string;
  reason: string;
  score: number;
  image?: string;
}

@Component({
  selector: 'app-chat-widget',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    MatChipsModule
  ],
  templateUrl: './chat-widget.component.html',
  styleUrls: ['./chat-widget.component.scss']
})
export class ChatWidgetComponent implements OnInit, OnDestroy {
  isOpen = false;
  isMinimized = false;
  messages: ChatMessage[] = [];
  messageControl = new FormControl('');
  isTyping = false;
  sessionId: string | null = null;
  chatHistory: ChatMessage[] = [];
  private messageIdCounter = 0;
  private chatSubscription: Subscription = new Subscription();

  quickActions = [
    { label: 'Recommend for Diabetes', value: 'I have diabetes, what fruits should I eat?' },
    { label: 'Heart Health', value: 'What fruits are good for heart health?' },
    { label: 'Immune Boost', value: 'Which fruits boost immunity?' },
    { label: 'Weight Loss', value: 'Fruits for weight management?' },
    { label: 'General Health', value: 'What are the healthiest fruits?' }
  ];

  constructor(private apiService: FruitopiaApiService, private chatService: ChatService) {}

  ngOnInit() {
    this.loadChatHistory();
    this.addWelcomeMessage();

    // Subscribe to chat service
    this.chatSubscription = this.chatService.chatOpen$.subscribe(isOpen => {
      this.isOpen = isOpen;
      if (this.isOpen && this.isMinimized) {
        this.isMinimized = false;
      }
    });
  }

  ngOnDestroy() {
    this.saveChatHistory();
    this.chatSubscription.unsubscribe();
  }

  toggleChat() {
    this.chatService.toggleChat();
  }

  minimizeChat() {
    this.isMinimized = !this.isMinimized;
  }

  closeChat() {
    this.isOpen = false;
    this.isMinimized = false;
    this.saveChatHistory();
  }

  sendMessage(text?: string) {
    const message = text || this.messageControl.value?.trim();
    if (!message) return;

    this.addMessage(message, 'user');
    this.messageControl.setValue('');
    this.isTyping = true;

    this.apiService.chatbotMessage(message, this.sessionId || undefined).subscribe({
      next: (response) => {
        this.isTyping = false;
        this.addMessage(response.response, 'bot');
        if (response.session_id && !this.sessionId) {
          this.sessionId = response.session_id;
        }
        this.saveChatHistory();
      },
      error: (error) => {
        this.isTyping = false;
        this.addMessage('Sorry, I\'m having trouble connecting right now. Please try again later.', 'bot');
        console.error('Chat error:', error);
      }
    });
  }

  sendQuickAction(action: any) {
    this.sendMessage(action.value);
  }

  clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
      this.messages = [];
      this.sessionId = null;
      this.chatHistory = [];
      localStorage.removeItem('fruitopia_chat_history');
      this.addWelcomeMessage();
    }
  }

  private addMessage(text: string, sender: 'user' | 'bot', type: 'text' | 'quick_actions' | 'fruit_card' = 'text', data?: any) {
    const message: ChatMessage = {
      id: this.generateMessageId(),
      text,
      sender,
      timestamp: new Date(),
      type,
      data
    };
    this.messages.push(message);
    this.chatHistory.push(message);
  }

  private addWelcomeMessage() {
    this.addMessage('🍎 Hello! I\'m your Fruitopia AI Assistant. I can help you find healthy fruits based on your health conditions, answer questions about nutrition, and provide personalized recommendations. What would you like to know?', 'bot');
    this.addQuickActions();
  }

  private addQuickActions() {
    setTimeout(() => {
      this.addMessage('Here are some quick questions to get started:', 'bot', 'quick_actions');
    }, 1000);
  }

  private generateMessageId(): string {
    return `msg_${++this.messageIdCounter}_${Date.now()}`;
  }

  private loadChatHistory() {
    const history = localStorage.getItem('fruitopia_chat_history');
    if (history) {
      try {
        this.chatHistory = JSON.parse(history).map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }));
        // Load last 10 messages
        this.messages = this.chatHistory.slice(-10);
      } catch (e) {
        console.error('Error loading chat history:', e);
      }
    }
  }

  private saveChatHistory() {
    localStorage.setItem('fruitopia_chat_history', JSON.stringify(this.chatHistory));
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  scrollToBottom() {
    setTimeout(() => {
      const chatMessages = document.querySelector('.chat-messages');
      if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }
    }, 100);
  }
}