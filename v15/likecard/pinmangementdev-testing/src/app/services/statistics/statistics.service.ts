import { HttpClient } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { serviceProviderSummary, merchantSummary } from 'src/models/statistics/statistics';
import { statisticsFilter } from 'src/models/statistics/statistics';

@Injectable({
  providedIn: 'root'
})
export class StatisticsService {

  constructor(
    private http: HttpClient,
    @Inject('BASE_URL') private baseurl: string
  ) {}

  getMerchantSummary(statisticsFilter:statisticsFilter): Observable<BaseResponse<merchantSummary>> {
    const body = {
      params: statisticsFilter,
    };
    return this.http.post<BaseResponse<merchantSummary>>(
      this.baseurl + '/exposed/merchant_stats',
      body
    );
  }
  getServiceProviderSummary(statisticsFilter: statisticsFilter): Observable<BaseResponse<serviceProviderSummary>> {
    const body = {
      params: statisticsFilter,
    };
    return this.http.post<BaseResponse<serviceProviderSummary>>(
      this.baseurl + '/exposed/service_provider_stats',
      body
    );
  }

}
