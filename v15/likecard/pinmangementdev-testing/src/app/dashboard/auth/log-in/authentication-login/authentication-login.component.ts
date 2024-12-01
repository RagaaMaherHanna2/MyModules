import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { AuthService } from 'src/app/services/auth.service';
import { environment } from 'src/environments/environment';
import { setAccessRights, setUser } from 'src/store/accessRightSlice';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-authentication-login',
  templateUrl: './authentication-login.component.html',
  styleUrls: ['./authentication-login.component.scss'],
})
export class AuthenticationLoginComponent {
  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private readonly store: Store<{}>
  ) {}
  OTPloginForm = this.formBuilder.group({
    login: [localStorage.getItem('login_email'), []],
    key: [JSON.parse(localStorage.getItem('key') || 'null') || '', []],
    authCode: ['', [Validators.required]],
  });
  get login() {
    return this.OTPloginForm.get('login')!;
  }
  get key() {
    return this.OTPloginForm.get('key')!;
  }
  get authCode(): string {
    return this.OTPloginForm.get('authCode')?.value || '';
  }

  set authCode(authCode: string) {
    this.OTPloginForm.get('authCode')?.setValue(authCode);
  }

  loginWithOTP(event: Event): void {
    this.store.dispatch(openLoadingDialog());
    this.authService
      .loginWithOtp(this.login.value, this.key.value, this.authCode)
      .subscribe((res) => {
        if (res.ok) {
          this.store.dispatch(closeLoadingDialog());
          localStorage.setItem(environment.TOKEN_KEY, res.result.token);
          localStorage.removeItem(environment.KEY);
          localStorage.removeItem(environment.LOGIN_EMAIL);
          this.authService.whoAmI().subscribe((res) => {
            if (res.ok) {
              localStorage.setItem(
                environment.CODES_ADDITIONAL_VALUE,
                res.result.codes_additional_value
              );
              localStorage.setItem(
                environment.USER_ROLES_KEY,
                JSON.stringify(res.result.roles)
              );
              localStorage.setItem(
                environment.USER_KEY,
                JSON.stringify(res.result)
              );
              localStorage.setItem(
                environment.CURRENCY_SYMBOL,
                res.result.currency_symbol
              );

              localStorage.setItem(environment.BALANCE_KEY, '0');
              this.store.dispatch(setAccessRights({ role: res.result.roles }));
              this.store.dispatch(setUser({ user: res.result }));
            }
          });
          this.store.dispatch(closeLoadingDialog());
          this.router.navigate(['/']);
        }
      });
  }
  onOtpChange(event: any) {
    if (event.length === 6) {
      this.authCode = event;
    }
  }
}
