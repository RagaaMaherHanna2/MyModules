import {
  MerchantProductInvitation,
  Product,
} from './../../../models/Product/models';
import {
  CreatePackage,
  PackageFilter,
  Package,
  CodeFilter,
  PackageCode,
  MerchantInvitation,
  MerchantInvitationFilter,
  PackageProductLine,
  inviteMerchantToProduct,
  EditMerchantInvitation,
} from './../../../models/package/models';
import { Inject, Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class PackageService {
  constructor(
    private http: HttpClient,
    @Inject('BASE_URL') private baseurl: string
  ) {}

  list(
    input: PackageFilter
  ): Observable<BaseResponse<GetListResponse<Package>>> {
    let body = {
      params: input,
    };
    return this.http.post<BaseResponse<GetListResponse<Package>>>(
      this.baseurl + '/exposed/list_packages',
      body
    );
  }
  details(params: {
    reference: string;
  }): Observable<BaseResponse<GetListResponse<Package>>> {
    let body = {
      params,
    };
    return this.http.post<BaseResponse<GetListResponse<Package>>>(
      this.baseurl + '/exposed/list_packages',
      body
    );
  }

  add(input: CreatePackage): Observable<BaseResponse<Package>> {
    let body = {
      jsonrpc: '2.0',
      params: input,
    };
    return this.http.post<BaseResponse<Package>>(
      this.baseurl + '/exposed/create_package',
      body
    );
  }
  edit(input: CreatePackage): Observable<BaseResponse<Package>> {
    let body = {
      jsonrpc: '2.0',
      params: input,
    };
    return this.http.post<BaseResponse<Package>>(
      this.baseurl + '/exposed/edit_package',
      body
    );
  }
  delete(input: number) {
    let body = {
      jsonrpc: '2.0',
      params: { id: input },
    };
    return this.http.post<any>(this.baseurl + '/exposed/package/delete', body);
  }
  listCode(input: CodeFilter) {
    let body = {
      jsonrpc: '2.0',
      params: input,
    };
    return this.http.post<BaseResponse<GetListResponse<PackageCode>>>(
      this.baseurl + '/exposed/get_package_codes',
      body
    );
  }
  getProductPackage(input: any) {
    let body = {
      jsonrpc: '2.0',
      params: input,
    };
    return this.http.post<BaseResponse<GetListResponse<Product>>>(
      this.baseurl + '/exposed/get_package_products',
      body
    );
  }
  merchantList(input: MerchantInvitationFilter) {
    let body = {
      jsonrpc: '2.0',
      params: input,
    };
    return this.http.post<BaseResponse<GetListResponse<MerchantInvitation>>>(
      this.baseurl + '/exposed/list_package_merchant_invites',
      body
    );
  }
  editInviteMerchant(
    input: EditMerchantInvitation
  ): Observable<BaseResponse<MerchantInvitation>> {
    let body = {
      jsonrpc: '2.0',
      params: input,
    };
    return this.http.post<BaseResponse<MerchantInvitation>>(
      this.baseurl + '/exposed/edit_merchant_package_invite',
      body
    );
  }
  inviteMerchant(
    params: inviteMerchantToProduct
  ): Observable<BaseResponse<MerchantInvitation>> {
    let body = {
      jsonrpc: '2.0',
      params,
    };
    return this.http.post<BaseResponse<MerchantInvitation>>(
      this.baseurl + '/exposed/merchant_package_invite',
      body
    );
  }

  addVouchers(params: {
    package: string;
    lines: PackageProductLine[];
  }): Observable<BaseResponse<{}>> {
    return this.http.post<BaseResponse<{}>>(
      `${environment.API_URL}/exposed/add_generation_request`,
      { params }
    );
  }

  inviteMerchantList(params: {
    invites: inviteMerchantToProduct[];
  }): Observable<BaseResponse<GetListResponse<MerchantInvitation>>> {
    return this.http.post<BaseResponse<GetListResponse<MerchantInvitation>>>(
      `${environment.API_URL}/exposed/merchant_package_invite_list`,
      { params }
    );
  }
}
