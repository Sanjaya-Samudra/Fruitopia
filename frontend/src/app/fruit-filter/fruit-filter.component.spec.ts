import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FruitFilterComponent } from './fruit-filter.component';

describe('FruitFilterComponent', () => {
  let component: FruitFilterComponent;
  let fixture: ComponentFixture<FruitFilterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FruitFilterComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FruitFilterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
