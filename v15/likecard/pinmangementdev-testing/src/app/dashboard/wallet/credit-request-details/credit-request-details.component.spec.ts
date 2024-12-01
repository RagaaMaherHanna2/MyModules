import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreditRequestDetailsComponent } from './credit-request-details.component';

describe('CreditRequestDetailsComponent', () => {
  let component: CreditRequestDetailsComponent;
  let fixture: ComponentFixture<CreditRequestDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreditRequestDetailsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreditRequestDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
