import { Component, Output, EventEmitter } from '@angular/core';
import { FruitopiaApiService } from '../fruitopia-api.service';

@Component({
  selector: 'app-fruit-filter',
  templateUrl: './fruit-filter.component.html',
  styleUrls: ['./fruit-filter.component.scss']
})
export class FruitFilterComponent {
  categories: string[] = ['all', 'antioxidant-rich', 'heart-healthy', 'immune-boosting'];
  selectedCategory: string = 'all';
  @Output() categoryChanged = new EventEmitter<string>();

  filterFruits() {
    this.categoryChanged.emit(this.selectedCategory);
  }
}
