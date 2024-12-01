import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FoodicsLoginComponent } from './foodics-login.component';

describe('FoodicsLoginComponent', () => {
  let component: FoodicsLoginComponent;
  let fixture: ComponentFixture<FoodicsLoginComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FoodicsLoginComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FoodicsLoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
