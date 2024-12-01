import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditPackageComponent } from './edit-package.component';

describe('EditPackageComponent', () => {
  let component: EditPackageComponent;
  let fixture: ComponentFixture<EditPackageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EditPackageComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditPackageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
