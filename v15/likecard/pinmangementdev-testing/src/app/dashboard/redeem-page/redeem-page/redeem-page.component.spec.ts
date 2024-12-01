import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RedeemPageComponent } from './redeem-page.component';

describe('RedeemPageComponent', () => {
  let component: RedeemPageComponent;
  let fixture: ComponentFixture<RedeemPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RedeemPageComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RedeemPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
