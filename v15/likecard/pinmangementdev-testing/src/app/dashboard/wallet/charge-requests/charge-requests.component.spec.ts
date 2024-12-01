import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChargeRequestsComponent } from './charge-requests.component';

describe('ChargeRequestsComponent', () => {
  let component: ChargeRequestsComponent;
  let fixture: ComponentFixture<ChargeRequestsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ChargeRequestsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ChargeRequestsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
