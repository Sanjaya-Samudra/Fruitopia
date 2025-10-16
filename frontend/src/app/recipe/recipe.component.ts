import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { FruitopiaApiService } from '../fruit/fruitopia-api.service';

interface Recipe {
  title: string;
  ingredients: string[];
  instructions: string[];
  nutritionalInfo: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  };
  prepTime: string;
  servings: number;
}

@Component({
  selector: 'app-recipe',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './recipe.component.html',
  styleUrl: './recipe.component.scss'
})
export class RecipeComponent implements OnInit {
  selectedFruits: string[] = [];
  dietaryPreferences: string[] = [];
  cuisineType: string = '';
  mealType: string = '';
  generatedRecipe: Recipe | null = null;
  isLoading: boolean = false;

  availableFruits = [
    'Apple', 'Banana', 'Orange', 'Strawberry', 'Blueberry', 'Mango',
    'Pineapple', 'Kiwi', 'Grape', 'Watermelon', 'Peach', 'Pear',
    'Cherry', 'Lemon', 'Lime', 'Avocado', 'Coconut', 'Fig'
  ];

  dietaryOptions = [
    'Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free', 'Keto', 'Paleo', 'Low-Carb'
  ];

  cuisineTypes = [
    'American', 'Italian', 'Mexican', 'Asian', 'Mediterranean', 'Indian', 'French'
  ];

  mealTypes = [
    'Breakfast', 'Lunch', 'Dinner', 'Snack', 'Dessert', 'Smoothie', 'Salad'
  ];

  constructor(private apiService: FruitopiaApiService) {}

  ngOnInit(): void {}

  toggleFruit(fruit: string): void {
    const index = this.selectedFruits.indexOf(fruit);
    if (index > -1) {
      this.selectedFruits.splice(index, 1);
    } else {
      this.selectedFruits.push(fruit);
    }
  }

  toggleDietaryPreference(pref: string): void {
    const index = this.dietaryPreferences.indexOf(pref);
    if (index > -1) {
      this.dietaryPreferences.splice(index, 1);
    } else {
      this.dietaryPreferences.push(pref);
    }
  }

  generateRecipe(): void {
    if (this.selectedFruits.length === 0) {
      alert('Please select at least one fruit!');
      return;
    }

    this.isLoading = true;
    this.generatedRecipe = null;

    const requestData = {
      fruits: this.selectedFruits,
      dietary_preferences: this.dietaryPreferences.length > 0 ? this.dietaryPreferences : null,
      cuisine_type: this.cuisineType || null,
      meal_type: this.mealType || null
    };

    this.apiService.generateRecipe(requestData).subscribe({
      next: (recipe: any) => {
        this.generatedRecipe = {
          title: recipe.title,
          ingredients: recipe.ingredients,
          instructions: recipe.instructions,
          nutritionalInfo: recipe.nutrition,
          prepTime: recipe.prep_time,
          servings: recipe.servings
        };
        this.isLoading = false;
      },
      error: (error: any) => {
        console.error('Recipe generation error:', error);
        // Fallback to mock recipe if API fails
        this.generatedRecipe = this.generateMockRecipe();
        this.isLoading = false;
      }
    });
  }

  private generateMockRecipe(): Recipe {
    const fruit = this.selectedFruits[0]; // Use first selected fruit for demo

    return {
      title: `${fruit} ${this.mealType || 'Delight'} Recipe`,
      ingredients: [
        `2 cups fresh ${fruit.toLowerCase()}s`,
        '1 cup Greek yogurt',
        '2 tablespoons honey',
        '1 teaspoon vanilla extract',
        '1/2 cup granola',
        'Fresh mint leaves for garnish'
      ],
      instructions: [
        `Wash and prepare the ${fruit.toLowerCase()}s by cutting them into bite-sized pieces.`,
        'In a mixing bowl, combine Greek yogurt, honey, and vanilla extract.',
        'Gently fold in the prepared fruits.',
        'Divide the mixture into serving bowls.',
        'Top with granola and fresh mint leaves.',
        'Serve immediately or chill for 30 minutes.'
      ],
      nutritionalInfo: {
        calories: 280,
        protein: 12,
        carbs: 45,
        fat: 8
      },
      prepTime: '15 minutes',
      servings: 2
    };
  }

  resetForm(): void {
    this.selectedFruits = [];
    this.dietaryPreferences = [];
    this.cuisineType = '';
    this.mealType = '';
    this.generatedRecipe = null;
  }

  getFruitIcon(fruit: string): string {
    const icons: { [key: string]: string } = {
      'Apple': '🍎',
      'Banana': '🍌',
      'Orange': '🍊',
      'Strawberry': '🍓',
      'Blueberry': '🫐',
      'Mango': '🥭',
      'Pineapple': '🍍',
      'Kiwi': '🥝',
      'Grape': '🍇',
      'Watermelon': '🍉',
      'Peach': '🍑',
      'Pear': '🍐',
      'Cherry': '🍒',
      'Lemon': '🍋',
      'Lime': '🍋',
      'Avocado': '🥑',
      'Coconut': '🥥',
      'Fig': '🫠'
    };
    return icons[fruit] || '🍽️';
  }

  getNutritionPercentage(nutrient: string, value: number): number {
    const maxValues = {
      calories: 500,
      protein: 30,
      carbs: 80,
      fat: 25
    };
    const max = maxValues[nutrient as keyof typeof maxValues] || 100;
    return Math.min((value / max) * 100, 100);
  }
}
