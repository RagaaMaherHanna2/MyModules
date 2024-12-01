import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FeesReportComponent } from './fees-report.component';

describe('FeesReportComponent', () => {
  let component: FeesReportComponent;
  let fixture: ComponentFixture<FeesReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FeesReportComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FeesReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
