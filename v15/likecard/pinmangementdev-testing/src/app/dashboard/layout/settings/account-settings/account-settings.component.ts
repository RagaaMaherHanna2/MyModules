import { Component, OnInit } from '@angular/core';
import { Store, createSelector } from '@ngrx/store';
import { MessageService } from 'primeng/api';
import { AuthService } from 'src/app/services/auth.service';
import { environment } from 'src/environments/environment';
import {
  accessRightFeature,
  setUser,
  setAccessRights,
} from 'src/store/accessRightSlice';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-account-settings',
  templateUrl: './account-settings.component.html',
  styleUrls: ['./account-settings.component.scss'],
})
export class AccountSettingsComponent implements OnInit {
  user$ = this.store.select(
    createSelector(accessRightFeature, (state) => state.user)
  );
  API_KEY: string = '';
  constructor(
    private store: Store,
    private authService: AuthService,
    private messageService: MessageService
  ) {}

  ngOnInit(): void {
    this.user$.subscribe((res) => {
      this.API_KEY = res.redeemly_api_key ?? '';
    });
  }
  generateNewKey(): void {
    this.store.dispatch(openLoadingDialog());
    this.authService.refreshAPIKey().subscribe((res) => {
      this.API_KEY = res.result.redeemly_api_key;
      this.authService.whoAmI().subscribe((res) => {
        localStorage.setItem(
          environment.CODES_ADDITIONAL_VALUE,
          res.result.codes_additional_value
        );
        localStorage.setItem(
          environment.CURRENCY_SYMBOL,
          res.result.currency_symbol
        );

        localStorage.setItem(environment.USER_KEY, JSON.stringify(res.result));
        this.store.dispatch(setUser({ user: res.result }));
        this.store.dispatch(closeLoadingDialog());

        if (res.ok) {
          localStorage.setItem(
            environment.USER_ROLES_KEY,
            JSON.stringify(res.result.roles)
          );
          localStorage.setItem(
            environment.USER_KEY,
            JSON.stringify(res.result)
          );

          localStorage.setItem(environment.BALANCE_KEY, '0');
          this.store.dispatch(setAccessRights({ role: res.result.roles }));
          this.store.dispatch(setUser({ user: res.result }));
        }
      });
    });
  }

  copy(): void {
    window.navigator.clipboard.writeText(this.API_KEY);
    this.messageService.add({
      summary: $localize`Copied`,
      detail: $localize`API Key copied`,
      severity: 'info',
    });
  }
}
