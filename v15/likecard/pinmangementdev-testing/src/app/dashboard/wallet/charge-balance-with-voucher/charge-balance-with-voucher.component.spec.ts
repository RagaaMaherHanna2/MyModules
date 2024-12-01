import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChargeBalanceWithVoucherComponent } from './charge-balance-with-voucher.component';

describe('ChargeBalanceWithVoucherComponent', () => {
  let component: ChargeBalanceWithVoucherComponent;
  let fixture: ComponentFixture<ChargeBalanceWithVoucherComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ChargeBalanceWithVoucherComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChargeBalanceWithVoucherComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
