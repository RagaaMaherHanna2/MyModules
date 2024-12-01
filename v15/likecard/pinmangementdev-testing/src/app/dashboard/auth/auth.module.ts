import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { AuthRoutingModule } from './auth-routing.module';
import { LogInComponent } from './log-in/log-in.component';
import { ReactiveFormsModule } from '@angular/forms';
import { SharedModule } from 'src/app/shared/shared.module';
import { PasswordModule } from 'primeng/password';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { ResetPasswordComponent } from './reset-password/reset-password.component';
import { VerifyResetPasswordComponent } from './verify-reset-password/verify-reset-password.component';
import { ChangePasswordComponent } from './log-in/change-password/change-password.component';
import { AuthenticationLoginComponent } from './log-in/authentication-login/authentication-login.component';
import { NgOtpInputModule } from  'ng-otp-input';

@NgModule({
  declarations: [
    LogInComponent,
    ChangePasswordComponent,
    ResetPasswordComponent,
    VerifyResetPasswordComponent,
    AuthenticationLoginComponent
  ],
  imports: [
    CommonModule,
    AuthRoutingModule,
    ReactiveFormsModule,
    SharedModule,
    PasswordModule,
    InputTextModule,
    ButtonModule,
    NgOtpInputModule
  ],
})
export class AuthModule {}
