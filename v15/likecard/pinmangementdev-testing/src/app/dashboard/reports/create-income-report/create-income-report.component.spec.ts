import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateIncomeReportComponent } from './create-income-report.component';

describe('CreateIncomeReportComponent', () => {
  let component: CreateIncomeReportComponent;
  let fixture: ComponentFixture<CreateIncomeReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreateIncomeReportComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateIncomeReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
