import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InviteMerchantComponent } from './invite-merchant.component';

describe('InviteMerchantComponent', () => {
  let component: InviteMerchantComponent;
  let fixture: ComponentFixture<InviteMerchantComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ InviteMerchantComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InviteMerchantComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
