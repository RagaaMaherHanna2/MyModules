import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PackageMerchantsComponent } from './package-merchants.component';

describe('PackageMerchantsComponent', () => {
  let component: PackageMerchantsComponent;
  let fixture: ComponentFixture<PackageMerchantsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PackageMerchantsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PackageMerchantsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
