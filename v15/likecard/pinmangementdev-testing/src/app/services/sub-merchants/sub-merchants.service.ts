import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { Observable } from 'rxjs';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { MerchantInvite, MerchantInviteResponse, MerchantsInviteList } from 'src/models/invites/invites.model';
import {Permission} from './../../../models/Product/models';

@Injectable({
  providedIn: 'root',
})
export class SubMerchantsService {
  constructor(private http: HttpClient) {}

  getCreatedSubMerchant(offset:number = 0,limit:number=environment.PAGE_SIZE , id: number=0): Observable<
  BaseResponse<GetListResponse<MerchantsInviteList>>
> {
  return this.http.post<BaseResponse<GetListResponse<MerchantsInviteList>>>(
    `${environment.API_URL}/exposed/auth/get_new_sub_merchants`,
    {params:{offset,limit, id}}
  );
}

  createSubMerchant(
    input: MerchantInvite
  ): Observable<BaseResponse<MerchantInviteResponse>> {
    return this.http.post<BaseResponse<MerchantInviteResponse>>(
      `${environment.API_URL}/exposed/auth/create_sub_merchant_account`,
      {params:input}
    );
  }

  getSubMerchant(id: number): Observable<
  BaseResponse<GetListResponse<MerchantsInviteList>>> {
  return this.http.post<BaseResponse<GetListResponse<MerchantsInviteList>>>(
    `${environment.API_URL}/exposed/auth/get_new_sub_merchants`,
    {params:{id}}
  );
}
assignPermissionToSubmerchant(codes: any[],sub_merchant: string): Observable<
  BaseResponse<GetListResponse<MerchantsInviteList>>> {
  return this.http.post<BaseResponse<GetListResponse<MerchantsInviteList>>>(
    `${environment.API_URL}/exposed/assign_permission_to_submerchant`,
    {params:{
      codes,
      sub_merchant
    }}
  );
}

  getSubMerchantListPermissions(sub_merchant: string): Observable<BaseResponse<GetListResponse<Permission>>> {
  return this.http.post<BaseResponse<GetListResponse<Permission>>>(
    `${environment.API_URL}/exposed/list_permission`,
    {params:{sub_merchant}}
  );
}

}
