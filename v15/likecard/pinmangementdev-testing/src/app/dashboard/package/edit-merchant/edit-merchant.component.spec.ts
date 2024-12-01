import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditMerchantComponent } from './edit-merchant.component';

describe('EditMerchantComponent', () => {
  let component: EditMerchantComponent;
  let fixture: ComponentFixture<EditMerchantComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EditMerchantComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditMerchantComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
