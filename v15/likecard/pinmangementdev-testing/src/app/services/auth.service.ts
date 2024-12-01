import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import {
  AuthenticateResponse,
  DashboardUser,
  TwoFactorAuthentication,
  Currency,
} from 'src/models/User';
import { NotificationItem } from 'src/models/dashboard/layout.model';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { GetListResponse } from 'src/models/responses/get-response.model';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  constructor(private httpService: HttpClient, private router: Router) {}

  logout() {
    this.logoutApi().subscribe((res) => {
      localStorage.removeItem(environment.CURRENCY_SYMBOL);
      localStorage.removeItem(environment.TOKEN_KEY);
      localStorage.removeItem(environment.USER_ROLES_KEY);
      localStorage.removeItem(environment.USER_KEY);
      localStorage.removeItem(environment.BALANCE_KEY);

      localStorage.removeItem('first_login');
      this.router.navigate(['/auth/login']);
    });
  }

  logoutApi(): Observable<BaseResponse<{}>> {
    return this.httpService.post<BaseResponse<any>>(
      `${environment.API_URL}/exposed/logout`,
      { params: {} }
    );
  }
  whoAmI(): Observable<BaseResponse<DashboardUser>> {
    return this.httpService.post<BaseResponse<DashboardUser>>(
      `${environment.API_URL}/exposed/auth/whoami`,
      {}
    );
  }
  enable2f(): Observable<BaseResponse<TwoFactorAuthentication>> {
    return this.httpService.post<BaseResponse<TwoFactorAuthentication>>(
      `${environment.API_URL}/exposed/login/enable2f`,
      {}
    );
  }

  login(
    email: string | null,
    password: string | null
  ): Observable<BaseResponse<AuthenticateResponse>> {
    const body = {
      params: {
        login: email,
        password,
      },
    };
    return this.httpService.post<BaseResponse<AuthenticateResponse>>(
      `${environment.API_URL}/exposed/auth/authenticate`,
      body
    );
  }
  active_enable2f(
    code: string | null,
    secret: string | null
  ): Observable<BaseResponse<AuthenticateResponse>> {
    const body = {
      params: {
        code,
        secret,
      },
    };
    return this.httpService.post<BaseResponse<AuthenticateResponse>>(
      `${environment.API_URL}/exposed/login/active_enable2f`,
      body
    );
  }

  disable_2f(): Observable<BaseResponse<TwoFactorAuthentication>> {
    return this.httpService.post<BaseResponse<TwoFactorAuthentication>>(
      `${environment.API_URL}/exposed/2f/disable`,
      {}
    );
  }
  refresh2f(
    refresh_route: string | null
  ): Observable<BaseResponse<TwoFactorAuthentication>> {
    const body = {
      params: {
        refresh_route,
      },
    };
    return this.httpService.post<BaseResponse<TwoFactorAuthentication>>(
      `${environment.API_URL}/exposed/login/refresh2f`,
      body
    );
  }
  activ_refresh2f(
    code: string | null
  ): Observable<BaseResponse<TwoFactorAuthentication>> {
    const body = {
      params: {
        code,
      },
    };
    return this.httpService.post<BaseResponse<TwoFactorAuthentication>>(
      `${environment.API_URL}/exposed/login/activ_refresh2f`,
      body
    );
  }

  activ_refresh2f_qr_code(
    code: string | null,
    secret: string | null
  ): Observable<BaseResponse<AuthenticateResponse>> {
    const body = {
      params: {
        code,
        secret,
      },
    };
    return this.httpService.post<BaseResponse<AuthenticateResponse>>(
      `${environment.API_URL}/exposed/login/activ_refresh2f_qr_code`,
      body
    );
  }

  loginWithOtp(
    login: string | null,
    key: string | null,
    totp_token: string | null
  ): Observable<BaseResponse<AuthenticateResponse>> {
    const body = {
      params: {
        login: login,
        key: key,
        totp_token: totp_token,
      },
    };
    return this.httpService.post<BaseResponse<AuthenticateResponse>>(
      `${environment.API_URL}/exposed/login/totp`,
      body
    );
  }

  refreshAPIKey(): Observable<BaseResponse<{ redeemly_api_key: string }>> {
    return this.httpService.post<BaseResponse<{ redeemly_api_key: string }>>(
      `${environment.API_URL}/exposed/auth/refresh_api_key`,
      { params: {} }
    );
  }

  resetPassword(params: {
    email: string;
    url: string;
  }): Observable<BaseResponse<DashboardUser>> {
    return this.httpService.post<BaseResponse<DashboardUser>>(
      `${environment.API_URL}/exposed/auth/reset_password`,
      { params }
    );
  }

  verifyResetPassword(params: {
    token: string;
    new_password: string;
  }): Observable<BaseResponse<{}>> {
    return this.httpService.post<BaseResponse<{}>>(
      `${environment.API_URL}/exposed/auth/reset_password_confirmed`,
      { params }
    );
  }

  changePassword(
    old_password: string | null,
    new_password: string | null
  ): Observable<BaseResponse<AuthenticateResponse>> {
    const body = {
      params: {
        old_password: old_password,
        new_password: new_password,
      },
    };
    return this.httpService.post<BaseResponse<AuthenticateResponse>>(
      `${environment.API_URL}/exposed/auth/change_password`,
      body
    );
  }

  getALlNotifications(): Observable<
    BaseResponse<GetListResponse<NotificationItem>>
  > {
    return this.httpService.post<
      BaseResponse<GetListResponse<NotificationItem>>
    >(`${environment.API_URL}/exposed/auth/get_notifications`, {});
  }
  markAllnotificationAsRead(ids: number[]): Observable<BaseResponse<any>> {
    console.log('ddd', ids);
    return this.httpService.post<BaseResponse<any>>(
      `${environment.API_URL}/exposed/auth/set_notifycation_readed`,
      {
        params: {
          ids,
        },
      }
    );
  }
  getAvailableCurrencies(): Observable<
    BaseResponse<GetListResponse<Currency>>
  > {
    return this.httpService.post<BaseResponse<GetListResponse<Currency>>>(
      `${environment.API_URL}/exposed/get_available_currencies`,
      {}
    );
  }
  getAllCurrencies(): Observable<BaseResponse<GetListResponse<Currency>>> {
    return this.httpService.post<BaseResponse<GetListResponse<Currency>>>(
      `${environment.API_URL}/exposed/get_all_currencies`,
      {}
    );
  }
}
