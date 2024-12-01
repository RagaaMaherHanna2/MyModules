import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import {
  SPNotificationsSettings,
  merchantNotificationsSettings,
} from 'src/models/User';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { GetListResponse } from 'src/models/responses/get-response.model';
import {
  spWebsiteKey,
  WebsiteApiKeysBody,
  WebsiteName,
} from 'src/models/settings/settings';
import { serviceProviderSummary } from 'src/models/statistics/statistics';

@Injectable({
  providedIn: 'root',
})
export class SettingsService {
  constructor(private httpService: HttpClient) {}
  updateMerchantSettings(
    params: merchantNotificationsSettings
  ): Observable<BaseResponse<any>> {
    return this.httpService.post<BaseResponse<any>>(
      `${environment.API_URL}/exposed/update_settings`,
      { params }
    );
  }
  updateServiceProviderSettings(
    params: SPNotificationsSettings
  ): Observable<BaseResponse<any>> {
    return this.httpService.post<BaseResponse<any>>(
      `${environment.API_URL}/exposed/update_settings`,
      { params }
    );
  }
  getMerchantSettings(): Observable<BaseResponse<any>> {
    return this.httpService.post<BaseResponse<merchantNotificationsSettings>>(
      `${environment.API_URL}/exposed/get_settings`,
      {}
    );
  }
  getServiceProviderSettings(): Observable<BaseResponse<any>> {
    return this.httpService.post<BaseResponse<SPNotificationsSettings>>(
      `${environment.API_URL}/exposed/get_settings`,
      {}
    );
  }

  getSpsWebsiteKeys(
    params: WebsiteApiKeysBody
  ): Observable<BaseResponse<GetListResponse<spWebsiteKey>>> {
    return this.httpService.post<BaseResponse<GetListResponse<spWebsiteKey>>>(
      `${environment.API_URL}/exposed/get_sp_websites_keys`,
      { params }
    );
  }
  generateWebsiteKey(params: WebsiteName): Observable<BaseResponse<any>> {
    return this.httpService.post<BaseResponse<any>>(
      `${environment.API_URL}/exposed/generate_website_key`,
      { params }
    );
  }
}
