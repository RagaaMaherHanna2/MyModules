import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PackageWizardStepsComponent } from './package-wizard-steps.component';

describe('PackageWizardStepsComponent', () => {
  let component: PackageWizardStepsComponent;
  let fixture: ComponentFixture<PackageWizardStepsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PackageWizardStepsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PackageWizardStepsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
