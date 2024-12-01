import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PackageWizardInviteMerchantsComponent } from './package-wizard-invite-merchants.component';

describe('PackageWizardInviteMerchantsComponent', () => {
  let component: PackageWizardInviteMerchantsComponent;
  let fixture: ComponentFixture<PackageWizardInviteMerchantsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PackageWizardInviteMerchantsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PackageWizardInviteMerchantsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
