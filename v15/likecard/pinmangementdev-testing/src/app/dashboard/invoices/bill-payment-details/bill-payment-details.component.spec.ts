import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BillPaymentDetailsComponent } from './bill-payment-details.component';

describe('BillPaymentDetailsComponent', () => {
  let component: BillPaymentDetailsComponent;
  let fixture: ComponentFixture<BillPaymentDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BillPaymentDetailsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BillPaymentDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
