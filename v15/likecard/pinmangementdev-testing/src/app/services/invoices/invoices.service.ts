import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import {
  RequestInvoiceBody,
  RequestInvoice,
  Bill,
} from 'src/models/invoices/invoices.model';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { BankTransferRequest } from 'src/models/wallet/models';

type PaginationFilter = {
  offset: number;
  limit: number;
  type: string;
};

@Injectable({
  providedIn: 'root',
})
export class InvoicesService {
  constructor(private httpService: HttpClient) { }

  requestInvoice(
    body: RequestInvoiceBody
  ): Observable<BaseResponse<RequestInvoice>> {
    return this.httpService.post<BaseResponse<RequestInvoice>>(
      `${environment.API_URL}/exposed/create_invoice_request`,
      {
        params: body,
      }
    );
  }

  listInvoices(
    params: PaginationFilter
  ): Observable<BaseResponse<GetListResponse<any>>> {
    return this.httpService.post<BaseResponse<GetListResponse<any>>>(
      `${environment.API_URL}/exposed/get_invoice_request_list`,
      {
        params,
      }
    );
  }
  merchantListInvoices(
    params: PaginationFilter
  ): Observable<BaseResponse<GetListResponse<any>>> {
    return this.httpService.post<BaseResponse<GetListResponse<any>>>(
      `${environment.API_URL}/exposed/get_merchant_invoices`,
      {
        params,
      }
    );
  }

  getBills(
    offset: number = 0, limit: number = environment.PAGE_SIZE, id: number = 0
  ): Observable<BaseResponse<GetListResponse<Bill>>> {
    return this.httpService.post<BaseResponse<GetListResponse<Bill>>>(`${environment.API_URL}/exposed/wallet/get_fees_invoices`,
      { params: { offset, limit, id } }
    );
  }
  getBillPaymentDetails(
    invoice_id: number = 0
  ): Observable<BaseResponse<GetListResponse<BankTransferRequest>>> {
    return this.httpService.post<BaseResponse<GetListResponse<BankTransferRequest>>>(`${environment.API_URL}/exposed/wallet/get_fees_invoice_payments`,
      { params: { invoice_id } }
    );
  }
  toggleShowOnMerchantDashboard(
   id: number = 0
  ): Observable<BaseResponse<GetListResponse<BankTransferRequest>>> {
    return this.httpService.post<BaseResponse<GetListResponse<BankTransferRequest>>>(`${environment.API_URL}/exposed/toggle_show_on_merchant_dashboard`,
      { params: { id } }
    );
  }


}
