import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FoodicsNewComponent } from './foodics-new.component';

describe('FoodicsNewComponent', () => {
  let component: FoodicsNewComponent;
  let fixture: ComponentFixture<FoodicsNewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FoodicsNewComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FoodicsNewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
