import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Store } from '@ngrx/store';
import { AuthService } from 'src/app/services/auth.service';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';
import { environment } from 'src/environments/environment';
import { setAccessRights, setUser } from 'src/store/accessRightSlice';
import { Router } from '@angular/router';

@Component({
  selector: 'app-change-password',
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.scss'],
})
export class ChangePasswordComponent {
  constructor(
    private formBuilder: FormBuilder,
    private store: Store,
    private authService: AuthService,
    private router: Router
  ) {}

  isFirstLogin = localStorage.getItem('first_login');
  changePasswordForm = this.formBuilder.group({
    old_password: ['', [Validators.required]],
    new_password: ['', [Validators.required]],
  });

  get old_password() {
    return this.changePasswordForm.get('old_password')!;
  }

  get new_password() {
    return this.changePasswordForm.get('new_password')!;
  }
  login(event: Event): void {
    this.store.dispatch(openLoadingDialog());
    this.authService
      .changePassword(this.old_password.value, this.new_password.value)
      .subscribe((res) => {
        if (res.ok) {
          if (this.isFirstLogin) {
            localStorage.setItem('first_login', JSON.stringify(false));
          }
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
              localStorage.setItem(environment.BALANCE_KEY, '0');
              localStorage.setItem(
                environment.CURRENCY_SYMBOL,
                res.result.currency_symbol
              );

              this.store.dispatch(setAccessRights({ role: res.result.roles }));
              this.store.dispatch(setUser({ user: res.result }));
            }
          });
          this.store.dispatch(closeLoadingDialog());
          this.router.navigate(['/']);
        }
      });
  }
}
