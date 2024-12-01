import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BankTransferPayComponent } from './bank-transfer-pay.component';

describe('BankTransferPayComponent', () => {
  let component: BankTransferPayComponent;
  let fixture: ComponentFixture<BankTransferPayComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BankTransferPayComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BankTransferPayComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
