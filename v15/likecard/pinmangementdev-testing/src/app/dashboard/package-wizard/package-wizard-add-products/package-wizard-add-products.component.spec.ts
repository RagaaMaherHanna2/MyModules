import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PackageWizardAddProductsComponent } from './package-wizard-add-products.component';

describe('PackageWizardAddProductsComponent', () => {
  let component: PackageWizardAddProductsComponent;
  let fixture: ComponentFixture<PackageWizardAddProductsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PackageWizardAddProductsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PackageWizardAddProductsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
