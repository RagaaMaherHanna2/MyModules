import { HttpClient } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Order, orderFilter } from 'src/models/orders/orders';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { GetListResponse } from 'src/models/responses/get-response.model';

@Injectable({
  providedIn: 'root'
})
export class OrdersService {
  constructor(
    private http: HttpClient,
    @Inject('BASE_URL') private baseurl: string
  ) {}

  getOrdersList(
    input: orderFilter
  ): Observable<BaseResponse<GetListResponse<Order>>> {
    let body = {
      params: input,
    };
    return this.http.post<BaseResponse<GetListResponse<Order>>>(
      this.baseurl + '/exposed/order_list',
      body
    );
  }

getOrderDetails(
  id: number
): Observable<BaseResponse<GetListResponse<Order>>> {
  const body = {
    params: { id: id },
  };
  return this.http.post<BaseResponse<GetListResponse<Order>>>(
    this.baseurl + '/exposed/order_list',
    body
  );
}
}