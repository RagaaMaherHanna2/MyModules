import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FoodicsConnectComponent } from './foodics-connect.component';

describe('FoodicsConnectComponent', () => {
  let component: FoodicsConnectComponent;
  let fixture: ComponentFixture<FoodicsConnectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FoodicsConnectComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FoodicsConnectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
