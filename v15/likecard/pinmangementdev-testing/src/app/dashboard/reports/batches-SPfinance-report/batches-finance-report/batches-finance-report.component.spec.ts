import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BatchesFinanceReportComponent } from './batches-finance-report.component';

describe('BatchesFinanceReportComponent', () => {
  let component: BatchesFinanceReportComponent;
  let fixture: ComponentFixture<BatchesFinanceReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BatchesFinanceReportComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BatchesFinanceReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
