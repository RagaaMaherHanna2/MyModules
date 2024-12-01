import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PackageReportComponent } from './package-report.component';

describe('PackageReportComponent', () => {
  let component: PackageReportComponent;
  let fixture: ComponentFixture<PackageReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PackageReportComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PackageReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
