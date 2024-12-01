import { Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';
import { Component, OnInit } from '@angular/core';
import { environment } from 'src/environments/environment';
import { Store } from '@ngrx/store';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';
import { FormBuilder, Validators } from '@angular/forms';
import { setAccessRights, setUser } from 'src/store/accessRightSlice';

@Component({
  selector: 'app-log-in',
  templateUrl: './log-in.component.html',
  styleUrls: ['./log-in.component.scss'],
})
export class LogInComponent {
  loginForm = this.formBuilder.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]],
  });

  get email() {
    return this.loginForm.get('email')!;
  }

  get password() {
    return this.loginForm.get('password')!;
  }
  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private readonly store: Store<{}>
  ) {}

  ngOnInit(): void {}
  login(event: Event): void {
    this.store.dispatch(openLoadingDialog());

    this.authService
      .login(this.email.value, this.password.value)
      .subscribe((res) => {
        if (res.ok) {
          localStorage.setItem(
            'first_login',
            JSON.stringify(res.result.first_login)
          );
          if (res.result.first_login) {
            localStorage.setItem(environment.TOKEN_KEY, res.result.token);
            this.store.dispatch(closeLoadingDialog());
            this.router.navigate(['/auth/change-password']);
          } else {
            if (res.result.is_2factor && res.result.key !== undefined) {
              this.store.dispatch(closeLoadingDialog());
              localStorage.setItem(environment.LOGIN_EMAIL, this.email.value!);
              localStorage.setItem(
                environment.KEY,
                JSON.stringify(res.result.key)
              );
              this.router.navigate(['/auth/authenticate']);
            } else {
              localStorage.setItem(environment.TOKEN_KEY, res.result.token);
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

                  this.store.dispatch(
                    setAccessRights({ role: res.result.roles })
                  );
                  this.store.dispatch(setUser({ user: res.result }));
                }
              });
              this.store.dispatch(closeLoadingDialog());
              this.router.navigate(['/']);
            }
          }
        }
      });
  }
}
