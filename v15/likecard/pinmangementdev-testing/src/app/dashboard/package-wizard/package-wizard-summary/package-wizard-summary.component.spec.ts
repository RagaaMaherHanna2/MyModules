import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PackageWizardSummaryComponent } from './package-wizard-summary.component';

describe('PackageWizardSummaryComponent', () => {
  let component: PackageWizardSummaryComponent;
  let fixture: ComponentFixture<PackageWizardSummaryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PackageWizardSummaryComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PackageWizardSummaryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
