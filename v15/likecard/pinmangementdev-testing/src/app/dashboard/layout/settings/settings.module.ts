import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SettingsRoutingModule } from './settings-routing.module';
import { DashboardSettingsComponent } from './dashboard-settings/dashboard-settings.component';
import { ReactiveFormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { RadioButtonModule } from 'primeng/radiobutton';
import { AccountSettingsComponent } from './account-settings/account-settings.component';
import { NotificationsComponent } from './notifications/notifications.component';
import { TwoFactorAuthComponent } from './two-factor-auth/two-factor-auth.component';
import { CardModule } from 'primeng/card';
import { DialogModule } from 'primeng/dialog';
import { ToggleButtonModule } from 'primeng/togglebutton';
import { EditNotificationsSettingsComponent } from './edit-notifications-settings/edit-notifications-settings.component';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { StepsModule } from 'primeng/steps';
import { NgOtpInputModule } from 'ng-otp-input';
import { InputNumberModule } from 'primeng/inputnumber';
import { InputTextModule } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { ApiKeysManagementComponent } from './api-keys-management/api-keys-management.component';

@NgModule({
  declarations: [
    DashboardSettingsComponent,
    AccountSettingsComponent,
    NotificationsComponent,
    EditNotificationsSettingsComponent,
    TwoFactorAuthComponent,
    ApiKeysManagementComponent,
  ],
  imports: [
    NgOtpInputModule,
    CommonModule,
    SettingsRoutingModule,
    RadioButtonModule,
    ButtonModule,
    ReactiveFormsModule,
    CardModule,
    ToggleButtonModule,
    ProgressSpinnerModule,
    DialogModule,
    StepsModule,
    InputNumberModule,
    InputTextModule,
    TableModule,
  ],
})
export class SettingsModule {}
