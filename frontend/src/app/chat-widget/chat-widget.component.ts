import { Component, ElementRef, ViewChild, OnInit, OnDestroy, HostListener } from '@angular/core';
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
  isDragging = false;
  dragStartX = 0;
  dragStartY = 0;
  panelX = 0;
  panelY = 0;

  @ViewChild('messageContainer') private messageContainer?: ElementRef;
  @ViewChild('inputField') private inputField?: ElementRef;
  @ViewChild('chatPanel') private chatPanel?: ElementRef;

  private subscription?: Subscription;

  constructor(private chatService: ChatService) {}

  ngOnInit() {
    this.subscription = this.chatService.chatOpen$.subscribe(open => {
      this.isOpen = open;
      this.messages = this.chatService.messages;
      if (open) {
        setTimeout(() => this.scrollToBottom(), 100);
        setTimeout(() => this.inputField?.nativeElement?.focus(), 300);
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

  formatMessage(text: string): string {
    if (!text) return '';
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/```(\w*)\n?([\s\S]*?)```/g, '<div class="code-block"><code>$2</code></div>')
      .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
      .replace(/\n- (.+)/g, '<li>$1</li>')
      .replace(/\n\d+\. (.+)/g, '<li>$1</li>')
      .replace(/\n{2,}/g, '</p><p>')
      .replace(/\n/g, '<br>');
    if (html.includes('<li>')) {
      html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    }
    return '<p>' + html + '</p>';
  }

  startDrag(event: MouseEvent) {
    this.isDragging = true;
    this.dragStartX = event.clientX - this.panelX;
    this.dragStartY = event.clientY - this.panelY;
    event.preventDefault();
  }

  @HostListener('document:mousemove', ['$event'])
  onDrag(event: MouseEvent) {
    if (!this.isDragging) return;
    this.panelX = event.clientX - this.dragStartX;
    this.panelY = event.clientY - this.dragStartY;
    const panel = this.chatPanel?.nativeElement;
    if (panel) {
      panel.style.transform = `translate(${this.panelX}px, ${this.panelY}px)`;
    }
  }

  @HostListener('document:mouseup')
  stopDrag() {
    this.isDragging = false;
  }

  private scrollToBottom() {
    if (this.messageContainer) {
      const el = this.messageContainer.nativeElement;
      el.scrollTop = el.scrollHeight;
    }
  }
}
