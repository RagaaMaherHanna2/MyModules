import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PackageWizardCreateComponent } from './package-wizard-create.component';

describe('PackageWizardCreateComponent', () => {
  let component: PackageWizardCreateComponent;
  let fixture: ComponentFixture<PackageWizardCreateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PackageWizardCreateComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PackageWizardCreateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
