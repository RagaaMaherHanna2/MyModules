import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { GetVendorsBody, Vendor } from 'src/models/vendors/vendor';

@Injectable({
  providedIn: 'root',
})
export class VendorsService {
  constructor(private http: HttpClient) {}

  getVendors(
    body: GetVendorsBody
  ): Observable<BaseResponse<GetListResponse<Vendor>>> {
    return this.http.post<BaseResponse<GetListResponse<Vendor>>>(
      `${environment.API_URL}/exposed/get_vendor_list`,
      { params: body }
    );
  }

  createVendor(name: string): Observable<BaseResponse<Vendor>> {
    return this.http.post<BaseResponse<Vendor>>(
      `${environment.API_URL}/exposed/create_vendor`,
      { params: { name: name } }
    );
  }
}
