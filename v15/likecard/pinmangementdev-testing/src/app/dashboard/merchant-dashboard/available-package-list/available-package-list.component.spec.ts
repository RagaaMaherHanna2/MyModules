import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AvailablePackageListComponent } from './available-package-list.component';

describe('AvailablePackageListComponent', () => {
  let component: AvailablePackageListComponent;
  let fixture: ComponentFixture<AvailablePackageListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AvailablePackageListComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AvailablePackageListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
