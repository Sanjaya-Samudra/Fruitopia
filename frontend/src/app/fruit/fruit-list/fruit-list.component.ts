import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { FruitopiaApiService } from '../fruitopia-api.service';
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-fruit-list',
  standalone: true,
  imports: [
    CommonModule,
    MatToolbarModule,
    MatCardModule,
    MatChipsModule,
    MatButtonModule,
    HttpClientModule
  ],
  templateUrl: './fruit-list.component.html',
  styleUrls: ['./fruit-list.component.scss']
})
export class FruitListComponent implements OnInit {
  fruits: any[] = [];
  constructor(private api: FruitopiaApiService) {}

  ngOnInit() {
    this.api.getFruits().subscribe((data: any) => {
      this.fruits = data;
    });
  }

  viewDetails(fruit: any) {
    // Implement navigation to fruit-detail or modal popup
    alert('Fruit details: ' + fruit.name);
  }

  openChatbot() {
    // Example: open a prompt for user message, send to backend, show response
    const userMessage = prompt('Ask Fruitopia Chatbot anything about healthy fruits!');
    if (userMessage) {
      this.api.chatbotMessage(userMessage).subscribe((res: any) => {
        alert('Chatbot says: ' + (res.response || 'No response'));
      });
    }
  }
}

