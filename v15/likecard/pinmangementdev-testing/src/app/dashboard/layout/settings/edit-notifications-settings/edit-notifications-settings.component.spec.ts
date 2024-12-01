import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditNotificationsSettingsComponent } from './edit-notifications-settings.component';

describe('EditNotificationsSettingsComponent', () => {
  let component: EditNotificationsSettingsComponent;
  let fixture: ComponentFixture<EditNotificationsSettingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EditNotificationsSettingsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditNotificationsSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
