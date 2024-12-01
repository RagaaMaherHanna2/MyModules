import { GetListResponse } from 'src/models/responses/get-response.model';
import { Observable } from 'rxjs';
import { BaseResponse } from 'src/models/responses/base-response.model';
import {
  MerchantProduct,
  MerchantProductDetails,
  MerchantProductFilter,
  PullCodeRequest,
  PullCodesResponse,
} from '../../../models/Merchant/models';
import { HttpClient } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
@Injectable({
  providedIn: 'root',
})
export class MerchantService {
  constructor(
    private http: HttpClient,
    @Inject('BASE_URL') private baseurl: string
  ) {}

  list(
    input: MerchantProductFilter
  ): Observable<BaseResponse<GetListResponse<MerchantProduct>>> {
    let body = {
      params: input,
    };

    return this.http.post<BaseResponse<GetListResponse<MerchantProduct>>>(
      this.baseurl + '/exposed/get_merchant_products',
      body
    );
  }

  detail(
    input: MerchantProductFilter
  ): Observable<BaseResponse<GetListResponse<MerchantProductDetails>>> {
    let body = {
      params: input,
    };

    return this.http.post<BaseResponse<GetListResponse<MerchantProductDetails>>>(
      this.baseurl + '/exposed/get_merchant_products',
      body
    );
  }

  pullCodes(input: PullCodeRequest) {
    let body = {
      params: input,
    };

    return this.http.post<BaseResponse<PullCodesResponse>>(
      this.baseurl + '/exposed/pull_codes_offline',
      body
    );
  }
}
