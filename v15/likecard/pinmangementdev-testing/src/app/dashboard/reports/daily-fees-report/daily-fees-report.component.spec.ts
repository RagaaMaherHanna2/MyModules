import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DailyFeesReportComponent } from './daily-fees-report.component';

describe('DailyFeesReportComponent', () => {
  let component: DailyFeesReportComponent;
  let fixture: ComponentFixture<DailyFeesReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DailyFeesReportComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DailyFeesReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
