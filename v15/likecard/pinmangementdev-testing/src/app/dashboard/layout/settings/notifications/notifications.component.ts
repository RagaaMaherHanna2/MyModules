import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { Store, createSelector } from '@ngrx/store';
import { SettingsService } from 'src/app/services/settings/settings.service';
import {
  SPNotificationsSettings,
  merchantNotificationsSettings,
} from 'src/models/User';
import { accessRightFeature } from 'src/store/accessRightSlice';

@Component({
  selector: 'app-notifications',
  templateUrl: './notifications.component.html',
  styleUrls: ['./notifications.component.scss'],
})
export class NotificationsComponent {
  constructor(
    private settingsService: SettingsService,
    private router: Router,
    private store: Store
  ) {}
  role$ = this.store.select(
    createSelector(accessRightFeature, (state) => state.role)
  );
  merchantNotificationSettings: merchantNotificationsSettings;
  spNotificationSettings: SPNotificationsSettings;
  isServiceProvider: boolean;
  ngOnInit() {
    this.role$.subscribe((roles) => {
      if (roles.includes('service_provider')) {
        this.isServiceProvider = true;
        this.settingsService.getServiceProviderSettings().subscribe((res) => {
          if (res.ok) this.spNotificationSettings = res.result;
        });
      }
      if (roles.includes('merchant') || roles.includes('submerchant')) {
        this.isServiceProvider = false;
        this.settingsService.getMerchantSettings().subscribe((res) => {
          if (res.ok) this.merchantNotificationSettings = res.result;
        });
      }
    });
  }

  edit() {
    this.router.navigate(['/dashboard/settings/notifications/edit']);
  }
  getNotificationValue(isEnabled: boolean) {
    if (isEnabled) {
      return $localize`Active`;
    } else {
      return $localize`Not Active`;
    }
  }
}
