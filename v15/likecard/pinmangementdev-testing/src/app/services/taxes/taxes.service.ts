
import {CreateTax,} from '../../../models/Taxes/models';
import { Injectable, Inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { Observable } from 'rxjs';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class TaxesService {
  constructor(
    private httpService: HttpClient,
    private http: HttpClient,
    @Inject('BASE_URL') private baseurl: string
  ) {}

  CreateTax(item: CreateTax): Observable<BaseResponse<any>> {
    const body = {
      params: item,
    };

    return this.http.post<BaseResponse<any>>(
      this.baseurl + '/exposed/create_tax',
      body
    );
  }

  listTaxes(
    params: any
  ): Observable<BaseResponse<GetListResponse<any>>> {
    return this.httpService.post<BaseResponse<GetListResponse<any>>>(
      `${environment.API_URL}/exposed/list_taxes`,
      {
        params,
      }
    );
  }

}
