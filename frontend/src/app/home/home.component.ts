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
  imageBase = '/api/vision/image?cls=';

  heroFruits = [
    { name: 'Blueberries', cls: 'blueberries' },
    { name: 'Avocado', cls: 'avocados' },
    { name: 'Strawberries', cls: 'strawberries' },
    { name: 'Mango', cls: 'mangos' },
  ];

  features = [
    { icon: 'auto_awesome', title: 'AI Recommendations', description: 'Get personalized fruit suggestions based on your health conditions and nutritional needs.', route: '/recommend', color: '#818cf8' },
    { icon: 'calendar_month', title: 'Meal Planner', description: 'AI-optimized weekly meal plans tailored to your health goals and dietary preferences.', route: '/meal-planner', color: '#a78bfa' },
    { icon: 'public', title: 'Fruit Culture', description: 'Global fruit cultivation, trade, sustainability data, and seasonal growing calendars.', route: '/fruit-culture', color: '#34d399' },
    { icon: 'hub', title: 'Research Graph', description: 'PubMed-cited evidence linking fruits to health outcomes with confidence scores.', route: '/knowledge-graph', color: '#22d3ee' },
    { icon: 'smart_toy', title: 'AI Nutrition Assistant', description: 'Chat with our RAG-powered AI about 30+ fruits, nutrition, and health.', action: 'chat', color: '#f472b6' },
    { icon: 'camera_alt', title: 'Smart Vision', description: 'Identify fruits and analyze ripeness, quality, and defects via computer vision.', route: '/vision', color: '#34d399' },
    { icon: 'restaurant', title: 'Recipe Generator', description: 'AI-generated recipes tailored to your fruits, dietary preferences, and goals.', route: '/recipes', color: '#f59e0b' },
    { icon: 'grid_view', title: 'Fruit Encyclopedia', description: 'Explore 30+ fruits with detailed nutrition, health benefits, and culinary uses.', route: '/gallery', color: '#22d3ee' },
    { icon: 'qr_code_scanner', title: 'Barcode Scanner', description: 'Scan barcodes to instantly identify fruit varieties, origins, and nutrition.', route: '/barcode', color: '#fb923c' },
    { icon: 'favorite', title: 'Wearables', description: 'Connect Apple Health, Fitbit, Garmin for personalized fruit recommendations.', route: '/health-platform', color: '#f472b6' },
    { icon: 'stars', title: 'Premium Plans', description: 'Unlock unlimited meal plans, advanced analytics, and enterprise API access.', route: '/premium', color: '#fbbf24' },
  ];

  showcaseFruits = [
    { name: 'Blueberries', slug: 'blueberries' }, { name: 'Apple', slug: 'apples' },
    { name: 'Banana', slug: 'bananas' }, { name: 'Orange', slug: 'oranges' },
    { name: 'Kiwi', slug: 'kiwifruit' }, { name: 'Strawberry', slug: 'strawberries' },
    { name: 'Mango', slug: 'mangos' }, { name: 'Pineapple', slug: 'pineapples' },
    { name: 'Avocado', slug: 'avocados' }, { name: 'Grapes', slug: 'grapes' },
    { name: 'Watermelon', slug: 'watermelons' }, { name: 'Cherries', slug: 'cherries' },
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

  openChat(): void {
    this.chatService.openChat();
  }
}
