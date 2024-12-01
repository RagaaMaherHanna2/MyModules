import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { Observable } from 'rxjs';
import { code } from 'src/models/serial/model';
import {
  PrepaidCode,
  PrepaidHistoryFilter,
  RedeemPrepaidCodeResponse,
  prepaidCheckBalanceRequest,
  RedeemPrepaidCodeRequest
} from 'src/models/prepaid/models';

@Injectable({
  providedIn: 'root',
})
export class CodeService {
  constructor(private http: HttpClient) {}

  check_codes(params: { codes: string[] }): Observable<BaseResponse<code[]>> {
    return this.http.post<BaseResponse<code[]>>(
      `${environment.API_URL}/exposed/check_and_redeem`,
      {
        params,
      }
    );
  }

  redeem(
    params: RedeemPrepaidCodeRequest
  ): Observable<BaseResponse<RedeemPrepaidCodeResponse>> {
    return this.http.post<BaseResponse<RedeemPrepaidCodeResponse>>(
      `${environment.API_URL}/exposed/redeem`,
      { params }
    );
  }

  checkPrepaidCodesBalance(
    params: prepaidCheckBalanceRequest
  ): Observable<BaseResponse<PrepaidCode[]>> {
    return this.http.post<BaseResponse<PrepaidCode[]>>(
      `${environment.API_URL}/exposed/check_balance_prepaid_offline`,
      {
        params,
      }
    );
  }
  getPrepaidRedeemHistory(
    input: PrepaidHistoryFilter
  ): Observable<BaseResponse<PrepaidCode>> {
    const body = {
      params: input,
    };
    return this.http.post<BaseResponse<PrepaidCode>>(
      `${environment.API_URL}/exposed/get_prepaid_redeem_history`,
      body
    );
  }
}
