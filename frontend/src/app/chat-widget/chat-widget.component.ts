import { Component, ElementRef, ViewChild, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ChatService, ChatMessage } from '../services/chat.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-chat-widget',
  standalone: true,
  imports: [CommonModule, FormsModule, MatIconModule, MatProgressSpinnerModule],
  templateUrl: './chat-widget.component.html',
  styleUrls: ['./chat-widget.component.scss']
})
export class ChatWidgetComponent implements OnInit, OnDestroy {
  isOpen = false;
  messages: ChatMessage[] = [];
  inputMessage = '';
  loading = false;

  @ViewChild('messageContainer') private messageContainer?: ElementRef;
  @ViewChild('inputField') private inputField?: ElementRef;

  private subscription?: Subscription;

  constructor(private chatService: ChatService) {}

  ngOnInit() {
    this.subscription = this.chatService.chatOpen$.subscribe(open => {
      this.isOpen = open;
      this.messages = this.chatService.messages;
      if (open) {
        setTimeout(() => this.scrollToBottom(), 100);
      }
    });
  }

  ngOnDestroy() {
    this.subscription?.unsubscribe();
  }

  toggleChat() {
    this.chatService.toggleChat();
  }

  closeChat() {
    this.chatService.closeChat();
  }

  sendMessage() {
    const msg = this.inputMessage.trim();
    if (!msg || this.loading) return;

    this.inputMessage = '';
    this.loading = true;

    this.chatService.sendMessage(msg).subscribe({
      next: (res) => {
        this.chatService.setSessionId(res.session_id);
        this.chatService.messages.push({
          role: 'bot',
          content: res.response,
          timestamp: new Date()
        });
        this.messages = [...this.chatService.messages];
        this.loading = false;
        setTimeout(() => this.scrollToBottom(), 50);
      },
      error: () => {
        this.chatService.messages.push({
          role: 'bot',
          content: "I'm sorry, I'm having trouble connecting. Please try again.",
          timestamp: new Date()
        });
        this.messages = [...this.chatService.messages];
        this.loading = false;
      }
    });
  }

  private scrollToBottom() {
    if (this.messageContainer) {
      const el = this.messageContainer.nativeElement;
      el.scrollTop = el.scrollHeight;
    }
  }
}
