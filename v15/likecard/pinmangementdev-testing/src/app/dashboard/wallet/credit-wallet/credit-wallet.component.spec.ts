import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreditWalletComponent } from './credit-wallet.component';

describe('CreditWalletComponent', () => {
  let component: CreditWalletComponent;
  let fixture: ComponentFixture<CreditWalletComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreditWalletComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreditWalletComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
