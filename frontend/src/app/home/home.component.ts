import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatGridListModule } from '@angular/material/grid-list';
import { ChatService } from '../services/chat.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatGridListModule
  ],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  featuredFruits = [
    {
      tagName: 'Blueberries',
      name: 'Blueberries',
      tagline: 'Antioxidant Powerhouse',
      image: 'https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=400&h=300&fit=crop&crop=center',
      benefits: ['Brain Health', 'Heart Protection', 'Anti-Inflammatory'],
      color: '#4A90E2'
    },
    {
      tagName: 'Avocados',
      name: 'Avocado',
      tagline: 'Healthy Fats Champion',
      image: 'https://cdn.pixabay.com/photo/2017/08/27/12/25/avocados-2685821_1280.jpg',
      benefits: ['Heart Health', 'Nutrient Absorption', 'Weight Management'],
      color: '#7ED321'
    },
    {
      tagName: 'Strawberries',
      name: 'Strawberries',
      tagline: 'Vitamin C Rich',
      image: 'https://cdn.pixabay.com/photo/2022/05/27/10/35/strawberry-7224875_1280.jpg',
      benefits: ['Immunity Boost', 'Skin Health', 'Antioxidants'],
      color: '#D0021B'
    },
    {
      tagName: 'Kiwifruit',
      name: 'Kiwi',
      tagline: 'Vitamin C Champion',
      image: 'https://images.unsplash.com/photo-1585059895524-72359e06133a?w=400&h=300&fit=crop&crop=center',
      benefits: ['Immunity', 'Digestive Health', 'Skin Glow'],
      color: '#8B4513'
    },
    {
      tagName: 'Mangos',
      name: 'Mango',
      tagline: 'Tropical Superfruit',
      image: 'https://cdn.pixabay.com/photo/2020/03/02/01/30/fruit-4894600_1280.jpg',
      benefits: ['Vitamin A', 'Digestive Enzymes', 'Energy Boost'],
      color: '#FFA500'
    },
    {
      tagName: 'Pineapples',
      name: 'Pineapple',
      tagline: 'Digestive Powerhouse',
      image: 'https://cdn.pixabay.com/photo/2020/04/21/18/02/pineapple-5074061_1280.jpg',
      benefits: ['Digestive Health', 'Immunity', 'Joint Health'],
      color: '#FFD700'
    }
  ];

  features = [
    {
      icon: 'smart_toy',
      title: 'AI-Powered Assistant',
      description: 'Get personalized fruit recommendations and nutritional advice from our advanced AI chatbot.',
      route: null,
      action: 'toggleChat',
      color: '#FF6B6B',
      comingSoon: false
    },
    {
      icon: 'camera_alt',
      title: 'Smart Recognition',
      description: 'Upload fruit images for instant identification and detailed nutritional information.',
      route: '/vision',
      color: '#4ECDC4',
      comingSoon: false
    },
    {
      icon: 'local_hospital',
      title: 'Health Recommendations',
      description: 'Discover fruits that support your specific health goals and medical conditions.',
      route: '/recommend',
      color: '#45B7D1',
      comingSoon: false
    },
    {
      icon: 'photo_library',
      title: 'Fruit Gallery',
      description: 'Explore our comprehensive collection of fruits with beautiful imagery and details.',
      route: '/gallery',
      color: '#96CEB4',
      comingSoon: false
    },
    {
      icon: 'search',
      title: 'Advanced Search',
      description: 'Find fruits by nutritional benefits, seasonal availability, or health conditions.',
      route: '/explore',
      color: '#FFEAA7',
      comingSoon: false
    },
    {
      icon: 'restaurant',
      title: 'Recipe Generator',
      description: 'Get AI-generated recipes using available fruits and your dietary preferences.',
      route: '/recipes',
      color: '#DDA0DD',
      comingSoon: false
    }
  ];

  stats = [
    { number: '30+', label: 'Fruits Available' },
    { number: '1000+', label: 'AI Conversations' },
    { number: '500+', label: 'Health Insights' },
    { number: '24/7', label: 'AI Assistant' }
  ];

  constructor(private chatService: ChatService) { }

  ngOnInit(): void {
  }

  scrollToFeatures(): void {
    const featuresSection = document.getElementById('features');
    if (featuresSection) {
      featuresSection.scrollIntoView({ behavior: 'smooth' });
    }
  }

  toggleChat(): void {
    this.chatService.toggleChat();
  }
}