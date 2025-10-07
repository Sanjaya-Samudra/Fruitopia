import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FruitDetailComponent } from './fruit-detail.component';

describe('FruitDetailComponent', () => {
  let component: FruitDetailComponent;
  let fixture: ComponentFixture<FruitDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FruitDetailComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FruitDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
