import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { Observable } from 'rxjs';
import { GetListResponse } from 'src/models/responses/get-response.model';
import {
  GetMerchantsBody,
  MerchantInvite,
  MerchantInviteResponse,
  MerchantsInviteList,
} from 'src/models/invites/invites.model';
import { IdName } from 'src/models/Merchant/models';

@Injectable({
  providedIn: 'root',
})
export class MerchantsService {
  constructor(private http: HttpClient) {}

  getInvitesList(
    offset: number = 0,
    limit: number = environment.PAGE_SIZE,
    service_provider_id = 0
  ): Observable<BaseResponse<GetListResponse<MerchantsInviteList>>> {
    return this.http.post<BaseResponse<GetListResponse<MerchantsInviteList>>>(
      `${environment.API_URL}/exposed/get_sp_invite_list`,
      { params: { offset, limit, service_provider_id } }
    );
  }
  getAccountantManagerSPs(
    offset: number = 0,
    limit: number = environment.PAGE_SIZE
  ): Observable<BaseResponse<GetListResponse<IdName>>> {
    return this.http.post<BaseResponse<GetListResponse<IdName>>>(
      `${environment.API_URL}/exposed/get_accountant_manager_sps`,
      { params: { offset, limit } }
    );
  }

  getCreatedMerchant(
    body: GetMerchantsBody
  ): Observable<BaseResponse<GetListResponse<MerchantsInviteList>>> {
    return this.http.post<BaseResponse<GetListResponse<MerchantsInviteList>>>(
      `${environment.API_URL}/exposed/auth/get_new_merchants`,
      { params: body }
    );
  }
  createMerchant(
    input: MerchantInvite
  ): Observable<BaseResponse<MerchantInviteResponse>> {
    return this.http.post<BaseResponse<MerchantInviteResponse>>(
      `${environment.API_URL}/exposed/auth/create_merchant_account`,
      { params: input }
    );
  }
}
