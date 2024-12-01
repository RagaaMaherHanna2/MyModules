import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RedeemHistoryDetailsComponent } from './redeem-history-details.component';

describe('RedeemHistoryDetailsComponent', () => {
  let component: RedeemHistoryDetailsComponent;
  let fixture: ComponentFixture<RedeemHistoryDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RedeemHistoryDetailsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RedeemHistoryDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
