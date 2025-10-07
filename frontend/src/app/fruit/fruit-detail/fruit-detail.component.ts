import { Component, Input, OnInit } from '@angular/core';
import { FruitopiaApiService } from '../fruitopia-api.service';

@Component({
  selector: 'app-fruit-detail',
  templateUrl: './fruit-detail.component.html',
  styleUrls: ['./fruit-detail.component.scss']
})
export class FruitDetailComponent implements OnInit {
  @Input() fruitName: string = '';
  fruit: any = null;
  constructor(private api: FruitopiaApiService) {}

  ngOnInit() {
    if (this.fruitName) {
      this.api.getFruitDetail(this.fruitName).subscribe((data: any) => {
        this.fruit = data;
      });
    }
  }
}
