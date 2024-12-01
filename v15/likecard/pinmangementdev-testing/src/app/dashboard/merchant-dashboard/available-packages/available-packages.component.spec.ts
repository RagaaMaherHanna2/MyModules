import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AvailablePackagesComponent } from './available-packages.component';

describe('AvailablePackagesComponent', () => {
  let component: AvailablePackagesComponent;
  let fixture: ComponentFixture<AvailablePackagesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AvailablePackagesComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AvailablePackagesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
