import { HttpClient } from '@angular/common/http';
import { Injectable, Inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { RedeemOperation, SecretCode } from 'src/models/Product/models';
import { RedeemHistoryWithFilter } from 'src/models/RedeemHistory/models';
import { ServiceProviderProfile } from 'src/models/User';
import {
  PrepaidRedeemBodyWithHash,
  RedeemPrepaidCodeResponse,
} from 'src/models/prepaid/models';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { SerialRedeemBodyWithHash, code } from 'src/models/serial/model';

@Injectable({
  providedIn: 'root',
})
export class RedeemService {
  constructor(
    private http: HttpClient,
    @Inject('BASE_URL') private baseurl: string
  ) {}

  authServiceProviderWithHash(
    sp_hash: string,
    sku: string
  ): Observable<BaseResponse<ServiceProviderProfile>> {
    return this.http.post<BaseResponse<ServiceProviderProfile>>(
      this.baseurl + '/exposed/auth/profile',
      {
        params: {
          sp_hash: sp_hash,
          sku: sku,
        },
      }
    );
  }
  checkCodesWithHash(params: {
    codes: SecretCode[];
    sp_hash: any;
    sku: string;
  }): Observable<BaseResponse<code[]>> {
    return this.http.post<BaseResponse<code[]>>(
      `${environment.API_URL}/exposed/check_and_redeem_with_hash`,
      {
        params,
      }
    );
  }
  redeemSerialWithHash(
    params: SerialRedeemBodyWithHash
  ): Observable<BaseResponse<code>> {
    return this.http.post<BaseResponse<code>>(
      `${environment.API_URL}/exposed/redeem_with_hash`,
      {
        params,
      }
    );
  }
  redeemPrepaidWithHash(
    params: PrepaidRedeemBodyWithHash
  ): Observable<BaseResponse<RedeemPrepaidCodeResponse>> {
    return this.http.post<BaseResponse<RedeemPrepaidCodeResponse>>(
      `${environment.API_URL}/exposed/redeem_with_hash`,
      {
        params,
      }
    );
  }
  getRedeemHistory(
    input: RedeemHistoryWithFilter
  ): Observable<BaseResponse<GetListResponse<RedeemOperation>>> {
    const body = {
      params: input,
    };
    return this.http.post<BaseResponse<GetListResponse<RedeemOperation>>>(
      `${environment.API_URL}/exposed/get_redemption_history`,
      body
    );
  }
}
