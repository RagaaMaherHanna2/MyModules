import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RedeemCodeComponent } from './redeem-code.component';

describe('RedeemCodeComponent', () => {
  let component: RedeemCodeComponent;
  let fixture: ComponentFixture<RedeemCodeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RedeemCodeComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RedeemCodeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
