import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateFeesReportComponent } from './create-fees-report.component';

describe('CreateFeesReportComponent', () => {
  let component: CreateFeesReportComponent;
  let fixture: ComponentFixture<CreateFeesReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreateFeesReportComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateFeesReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
