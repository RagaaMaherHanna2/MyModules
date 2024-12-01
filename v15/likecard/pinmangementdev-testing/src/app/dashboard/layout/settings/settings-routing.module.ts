import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardSettingsComponent } from './dashboard-settings/dashboard-settings.component';
import { AccountSettingsComponent } from './account-settings/account-settings.component';
import { NotificationsComponent } from './notifications/notifications.component';
import { TwoFactorAuthComponent } from './two-factor-auth/two-factor-auth.component';
import { EditNotificationsSettingsComponent } from './edit-notifications-settings/edit-notifications-settings.component';
import { ApiKeysManagementComponent } from './api-keys-management/api-keys-management.component';

const routes: Routes = [
  {
    path: '',
    children: [
      {
        path: '',
        component: DashboardSettingsComponent,
      },
      {
        path: 'account',
        component: AccountSettingsComponent,
      },
      {
        path: 'notifications',
        component: NotificationsComponent,
      },
      {
        path: 'notifications/edit',
        component: EditNotificationsSettingsComponent,
      },
      {
        path: 'Two-Factor-Authentication',
        component: TwoFactorAuthComponent,
      },
      {
        path: 'api-keys-management',
        component: ApiKeysManagementComponent,
      },
    ],
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class SettingsRoutingModule {}
