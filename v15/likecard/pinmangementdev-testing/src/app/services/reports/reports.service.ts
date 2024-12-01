import {
  CreateFeesReportBody,
  CreateIncomeReportBody,
  CreateSalesReport,
  DailyFeesReportbody,
} from '../../../models/Reports/models';
import { Injectable, Inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { Observable } from 'rxjs';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ReportsService {
  constructor(
    private httpService: HttpClient,
    private http: HttpClient,
    @Inject('BASE_URL') private baseurl: string
  ) {}

  createSalesReport(item: CreateSalesReport): Observable<BaseResponse<any>> {
    const body = {
      params: item,
    };

    return this.http.post<BaseResponse<any>>(
      this.baseurl + '/exposed/create_detail_sales_report',
      body
    );
  }
  createIncomeReport(
    item: CreateIncomeReportBody
  ): Observable<BaseResponse<any>> {
    const body = {
      params: item,
    };

    return this.http.post<BaseResponse<any>>(
      this.baseurl + '/exposed/create_daily_income_report',
      body
    );
  }
  createFeesReport(item: CreateFeesReportBody): Observable<BaseResponse<any>> {
    const body = {
      params: item,
    };

    return this.http.post<BaseResponse<any>>(
      this.baseurl + '/exposed/create_pull_fees_report',
      body
    );
  }

  listSalesReports(
    params: any
  ): Observable<BaseResponse<GetListResponse<any>>> {
    return this.httpService.post<BaseResponse<GetListResponse<any>>>(
      `${environment.API_URL}/exposed/get_detail_sales_report`,
      {
        params,
      }
    );
  }
  listIncomeReports(
    params: any
  ): Observable<BaseResponse<GetListResponse<any>>> {
    return this.httpService.post<BaseResponse<GetListResponse<any>>>(
      `${environment.API_URL}/exposed/get_daily_income_report`,
      {
        params,
      }
    );
  }
  listFeesReports(params: any): Observable<BaseResponse<GetListResponse<any>>> {
    return this.httpService.post<BaseResponse<GetListResponse<any>>>(
      `${environment.API_URL}/exposed/get_pull_fees_report`,
      {
        params,
      }
    );
  }
  listDailyFeesReports(
    params: DailyFeesReportbody
  ): Observable<BaseResponse<GetListResponse<any>>> {
    return this.httpService.post<BaseResponse<GetListResponse<any>>>(
      `${environment.API_URL}/exposed/daily_pull_redeem_fees_report`,
      {
        params,
      }
    );
  }
}
