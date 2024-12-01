import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListPackageComponent } from './list-package.component';

describe('ListPackageComponent', () => {
  let component: ListPackageComponent;
  let fixture: ComponentFixture<ListPackageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ListPackageComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListPackageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
