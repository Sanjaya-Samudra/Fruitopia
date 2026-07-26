import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { ChatService } from '../services/chat.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule, RouterModule,
    MatCardModule, MatButtonModule, MatIconModule
  ],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent {
  heroFruits = [
    { name: 'Blueberries', image: 'https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=300&h=300&fit=crop' },
    { name: 'Avocado', image: 'https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=300&h=300&fit=crop' },
    { name: 'Strawberries', image: 'https://images.unsplash.com/photo-1601004890684-d8cbf643f5f2?w=300&h=300&fit=crop' },
    { name: 'Mango', image: 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=300&h=300&fit=crop' },
  ];

  features = [
    {
      icon: 'auto_awesome',
      title: 'AI Recommendations',
      description: 'Get personalized fruit suggestions based on your health conditions, preferences, and nutritional needs.',
      route: '/recommend',
      color: '#818cf8',
    },
    {
      icon: 'smart_toy',
      title: 'AI Nutrition Assistant',
      description: 'Chat with our RAG-powered AI that answers questions from a knowledge base of 30+ fruits.',
      action: 'chat',
      color: '#f472b6',
    },
    {
      icon: 'calendar_month',
      title: 'Meal Planner',
      description: 'AI-optimized weekly meal plans tailored to your health goals, dietary preferences, and nutritional targets.',
      route: '/meal-planner',
      color: '#a78bfa',
    },
    {
      icon: 'public',
      title: 'Fruit Culture',
      description: 'Explore global fruit cultivation, trade routes, sustainability data, and seasonal growing calendars.',
      route: '/fruit-culture',
      color: '#34d399',
    },
    {
      icon: 'hub',
      title: 'Research Graph',
      description: 'PubMed-cited evidence linking fruits to health outcomes with confidence scores and effect sizes.',
      route: '/knowledge-graph',
      color: '#22d3ee',
    },
    {
      icon: 'camera_alt',
      title: 'Smart Vision',
      description: 'Identify fruits and analyze ripeness, quality, and defects using computer vision.',
      route: '/vision',
      color: '#34d399',
    },
    {
      icon: 'restaurant',
      title: 'Recipe Generator',
      description: 'Discover AI-generated recipes tailored to your fruits, dietary preferences, and health goals.',
      route: '/recipes',
      color: '#f59e0b',
    },
    {
      icon: 'grid_view',
      title: 'Fruit Encyclopedia',
      description: 'Explore 30+ fruits with detailed nutrition, health benefits, culinary uses, and cultivation info.',
      route: '/gallery',
      color: '#22d3ee',
    },
    {
      icon: 'qr_code_scanner',
      title: 'Barcode Scanner',
      description: 'Scan or enter barcodes to instantly identify fruits, varieties, countries of origin, and nutrition.',
      route: '/barcode',
      color: '#fb923c',
    },
    {
      icon: 'favorite',
      title: 'Wearables Integration',
      description: 'Connect Apple Health, Fitbit, Garmin, Whoop, Oura to get personalized fruit recommendations from your vitals.',
      route: '/health-platform',
      color: '#f472b6',
    },
    {
      icon: 'stars',
      title: 'Premium Plans',
      description: 'Unlock unlimited meal plans, advanced analytics, and enterprise API access.',
      route: '/premium',
      color: '#fbbf24',
    },
    {
      icon: 'question_answer',
      title: 'AI Chatbot',
      description: 'Ask anything about fruits, diseases, nutrition, and get evidence-based answers instantly.',
      action: 'chat',
      color: '#818cf8',
    },
  ];

  showcaseFruits = [
    { name: 'Blueberries', slug: 'blueberries', image: 'https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=200&h=200&fit=crop' },
    { name: 'Apple', slug: 'apples', image: 'https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=200&h=200&fit=crop' },
    { name: 'Banana', slug: 'bananas', image: 'https://images.unsplash.com/photo-1571771894821-ce9b6ba11aa8?w=200&h=200&fit=crop' },
    { name: 'Orange', slug: 'oranges', image: 'https://images.unsplash.com/photo-1547514701-42782101795e?w=200&h=200&fit=crop' },
    { name: 'Kiwi', slug: 'kiwifruit', image: 'https://images.unsplash.com/photo-1585059895524-72359e06133a?w=200&h=200&fit=crop' },
    { name: 'Strawberry', slug: 'strawberries', image: 'https://images.unsplash.com/photo-1601004890684-d8cbf643f5f2?w=200&h=200&fit=crop' },
    { name: 'Mango', slug: 'mangos', image: 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=200&h=200&fit=crop' },
    { name: 'Pineapple', slug: 'pineapples', image: 'https://images.unsplash.com/photo-1550258987-190a2d41a8ba?w=200&h=200&fit=crop' },
    { name: 'Avocado', slug: 'avocados', image: 'https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=200&h=200&fit=crop' },
    { name: 'Grapes', slug: 'grapes', image: 'https://images.unsplash.com/photo-1537640538966-79f369143f8b?w=200&h=200&fit=crop' },
    { name: 'Watermelon', slug: 'watermelons', image: 'https://images.unsplash.com/photo-1563114771-0b7e3a1e4f5a?w=200&h=200&fit=crop' },
    { name: 'Cherries', slug: 'cherries', image: 'https://images.unsplash.com/photo-1528821128474-27c963b3c7e0?w=200&h=200&fit=crop' },
  ];

  marqueeItems = [
    { icon: '🍎', text: 'Apple - 95 cal, rich in fiber' },
    { icon: '🫐', text: 'Blueberry - Antioxidant powerhouse' },
    { icon: '🍌', text: 'Banana - 422mg potassium' },
    { icon: '🍊', text: 'Orange - 53mg Vitamin C' },
    { icon: '🥝', text: 'Kiwi - More Vitamin C than oranges' },
    { icon: '🍓', text: 'Strawberry - Ellagic acid' },
    { icon: '🥑', text: 'Avocado - Healthy monounsaturated fats' },
    { icon: '🍍', text: 'Pineapple - Bromelain enzyme' },
    { icon: '🍇', text: 'Grape - Resveratrol' },
    { icon: '🍑', text: 'Peach - Vitamin A & C' },
  ];

  constructor(private chatService: ChatService) {}

  scrollToFeatures(): void {
    const el = document.getElementById('features');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  }

  navigateFeature(feature: any): void {
    if (feature.action === 'chat') {
      this.openChat();
    } else if (feature.route) {
      // Router navigation is handled by routerLink
    }
  }

  openChat(): void {
    this.chatService.openChat();
  }
}
