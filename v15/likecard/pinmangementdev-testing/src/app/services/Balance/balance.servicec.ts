import {
  FilterSelectionData,
  SalesReport,
  SalesReportFilter,
} from './../../../models/balance/models';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { Observable } from 'rxjs';
import { BaseResponse } from 'src/models/responses/base-response.model';
import {
  TransactionLog,
  TransactionLogFilter,
} from '../../../models/balance/models';
import { HttpClient } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
@Injectable({
  providedIn: 'root',
})
export class BalanceService {
  constructor(
    private http: HttpClient,
    @Inject('BASE_URL') private baseurl: string
  ) {}

  list(
    input: SalesReportFilter
  ): Observable<BaseResponse<GetListResponse<SalesReport>>> {
    let body = {
      params: input,
    };
    return this.http.post<BaseResponse<GetListResponse<SalesReport>>>(
      this.baseurl + '/exposed/wallet/get_balance_report',
      body
    );
  }
  getFilterData() {
    let body = {
      params: {},
    };
    return this.http.post<BaseResponse<FilterSelectionData>>(
      this.baseurl + '/exposed/wallet/get_balance_report_data',
      body
    );
  }
}
