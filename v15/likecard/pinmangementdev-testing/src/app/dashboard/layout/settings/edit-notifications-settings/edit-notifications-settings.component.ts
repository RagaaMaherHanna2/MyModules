import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { Store, createSelector } from '@ngrx/store';
import { MessageService } from 'primeng/api';
import { SettingsService } from 'src/app/services/settings/settings.service';
import { environment } from 'src/environments/environment';
import {
  SPNotificationsSettings,
  merchantNotificationsSettings,
} from 'src/models/User';
import { accessRightFeature } from 'src/store/accessRightSlice';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-edit-notifications-settings',
  templateUrl: './edit-notifications-settings.component.html',
  styleUrls: ['./edit-notifications-settings.component.scss'],
})
export class EditNotificationsSettingsComponent {
  constructor(
    private formBuilder: FormBuilder,
    private settingsService: SettingsService,
    private store: Store,
    private messageService: MessageService,
    private router: Router
  ) {}
  merchantNotificationsSettings: merchantNotificationsSettings;
  spNotificationsSettings: SPNotificationsSettings;
  sp_hash = JSON.parse(localStorage.getItem(environment.USER_KEY) ?? '{}')[
    'sp_hash'
  ];
  balanceNotificationForm = this.formBuilder.group({
    balance_limit: [, [Validators.min(0)]],
    enable_balance_notification: [false],
    balance_notification_to_email: [, Validators.email],
  });
  stockNotificationsForm = this.formBuilder.group({
    stock_limit: [, [Validators.min(0)]],
    enable_stock_notification: [false],
    stock_notification_to_email: [, Validators.email],
  });
  role$ = this.store.select(
    createSelector(accessRightFeature, (state) => state.role)
  );
  user$ = this.store.select(
    createSelector(accessRightFeature, (state) => state.user)
  );
  userEmail: string;

  isServiceProvider: boolean;
  ngOnInit() {
    this.user$.subscribe((user) => {
      this.userEmail = user.email;
    });

    this.role$.subscribe((roles) => {
      if (roles.includes('service_provider')) {
        this.isServiceProvider = true;

        this.settingsService.getServiceProviderSettings().subscribe((res) => {
          if (res.ok) {
            let stock_notification_to_email =
              res.result.stock_notification_to_email !== ''
                ? res.result.stock_notification_to_email
                : this.userEmail;
            this.spNotificationsSettings = res.result;
            this.stockNotificationsForm.patchValue({
              stock_limit: res.result.enable_low_stock_notification
                ? res.result.stock_limit
                : 0,
              enable_stock_notification:
                res.result.enable_low_stock_notification,
              stock_notification_to_email: res.result
                .enable_low_stock_notification
                ? stock_notification_to_email
                : '',
            });
          }
        });
      }

      if (roles.includes('merchant') || roles.includes('submerchant')) {
        this.isServiceProvider = false;
        this.settingsService.getMerchantSettings().subscribe((res) => {
          if (res.ok) {
            this.merchantNotificationsSettings = res.result;
            let balance_notification_to_email =
              res.result.balance_notification_to_email !== ''
                ? res.result.balance_notification_to_email
                : this.userEmail;
            this.balanceNotificationForm.patchValue({
              balance_limit: res.result.enable_low_balance_notification
                ? res.result.balance_limit
                : 0,
              enable_balance_notification:
                res.result.enable_low_balance_notification,
              balance_notification_to_email: res.result
                .enable_low_balance_notification
                ? balance_notification_to_email
                : '',
            });
          }
        });
      }
    });
  }
  submitStock() {
    this.store.dispatch(openLoadingDialog());
    let value = this.stockNotificationsForm.value;
    let stock_limit = value.stock_limit! as number;
    let enable_stock_notification = value.enable_stock_notification as boolean;
    let stock_notification_to_email = value.stock_notification_to_email
      ? value.stock_notification_to_email
      : this.userEmail;

    this.settingsService
      .updateServiceProviderSettings({
        stock_limit: enable_stock_notification ? stock_limit : 0,
        enable_low_stock_notification: enable_stock_notification,
        stock_notification_to_email: enable_stock_notification
          ? stock_notification_to_email
          : '',
      })
      .subscribe((res) => {
        this.store.dispatch(closeLoadingDialog());
        if (res.ok) {
          this.messageService.add({
            severity: 'success',
            summary: $localize`Successful`,
            detail: $localize`Updated Successfully`,
            life: 3000,
          });
          this.router.navigate(['/dashboard/settings/notifications']);
        }
      });
  }
  submitBalance() {
    this.store.dispatch(openLoadingDialog());
    let value = this.balanceNotificationForm.value;
    let balance_limit = value.balance_limit! as number;
    let enable_balance_notification =
      value.enable_balance_notification as boolean;
    let balance_notification_to_email = value.balance_notification_to_email
      ? value.balance_notification_to_email
      : this.userEmail;
    this.settingsService
      .updateMerchantSettings({
        balance_limit: enable_balance_notification ? balance_limit : 0,
        enable_low_balance_notification: enable_balance_notification,
        balance_notification_to_email: enable_balance_notification
          ? balance_notification_to_email
          : '',
      })
      .subscribe((res) => {
        this.store.dispatch(closeLoadingDialog());
        if (res.ok) {
          this.messageService.add({
            severity: 'success',
            summary: $localize`Successful`,
            detail: $localize`Updated Successfully`,
            life: 3000,
          });
          this.router.navigate(['/dashboard/settings/notifications']);
        }
      });
  }
}
