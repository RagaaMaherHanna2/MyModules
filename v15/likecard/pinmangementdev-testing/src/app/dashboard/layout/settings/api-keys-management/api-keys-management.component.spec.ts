import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ApiKeysManagementComponent } from './api-keys-management.component';

describe('ApiKeysManagementComponent', () => {
  let component: ApiKeysManagementComponent;
  let fixture: ComponentFixture<ApiKeysManagementComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ApiKeysManagementComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ApiKeysManagementComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
