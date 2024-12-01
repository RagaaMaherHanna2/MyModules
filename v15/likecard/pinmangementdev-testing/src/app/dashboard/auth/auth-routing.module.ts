import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LogInComponent } from './log-in/log-in.component';
import { ResetPasswordComponent } from './reset-password/reset-password.component';
import { VerifyResetPasswordComponent } from './verify-reset-password/verify-reset-password.component';
import { ChangePasswordComponent } from './log-in/change-password/change-password.component';
import { GuestGuard } from 'src/app/guards/guest.guard';
import { AuthenticationLoginComponent } from './log-in/authentication-login/authentication-login.component';
import { TwoFactorAuthGuard } from 'src/app/guards/two-factor-auth.guard';

const routes: Routes = [
  {
    path: '',
    children: [
      {
        path: 'login',
        component: LogInComponent,
        canMatch: [GuestGuard],
      },
      {
        path: 'change-password',
        component: ChangePasswordComponent,
      },
      {
        path: 'reset',
        component: ResetPasswordComponent,
      },
      {
        path: 'verify',
        component: VerifyResetPasswordComponent,
      },
      {
        path: 'authenticate',
        component: AuthenticationLoginComponent,
        canMatch: [TwoFactorAuthGuard],
      },
    ],
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class AuthRoutingModule {}
