import { BankTransferFilter } from './../../../models/wallet/models';
import {
  BankDetails,
  BankTransfer,
  BankTransferRequest,
} from 'src/models/wallet/models';
import { Inject, Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { ListFilter } from 'src/models/list-filter';
import { environment } from 'src/environments/environment';
import { Store } from '@ngrx/store';
import { setBalance } from 'src/store/balanceSlice';

@Injectable({
  providedIn: 'root',
})
export class WalletService {
  constructor(
    private http: HttpClient,
    @Inject('BASE_URL') private baseurl: string,
    private store: Store
  ) { }


  addBankTransfer(input: BankTransfer) {
    let body = {
      jsonrpc: '2.0',
      params: input,
    };
    return this.http.post<any>(
      this.baseurl + '/exposed/wallet/create_bank_transfer_request',
      body
    );
  }
  getServiceProviderChargeRequests(
    input: BankTransferFilter
  ): Observable<BaseResponse<GetListResponse<BankTransferRequest>>> {
    let body = {
      jsonrpc: '2.0',
      params: input,
    };
    return this.http.post<BaseResponse<GetListResponse<BankTransferRequest>>>(
      this.baseurl + '/exposed/wallet/get_sp_charge_request',
      body
    );
  }
  getServiceProviderChargeRequestsDetails(
    id: number
  ): Observable<BaseResponse<GetListResponse<BankTransferRequest>>> {
    const body = {
      params: { id: id },
    };
    return this.http.post<BaseResponse<GetListResponse<BankTransferRequest>>>(
      this.baseurl + '/exposed/wallet/get_sp_charge_request',
      body
    );
  }

  getMerchantChargeRequests(
    input: BankTransferFilter
  ): Observable<BaseResponse<GetListResponse<BankTransferRequest>>> {
    let body = {
      jsonrpc: '2.0',
      params: input,
    };
    return this.http.post<BaseResponse<GetListResponse<BankTransferRequest>>>(
      this.baseurl + '/exposed/wallet/get_merchant_bank_transfer_list',
      body
    );
  }

  addBankInformation(
    input: BankDetails
  ): Observable<BaseResponse<BankDetails>> {
    let body = {
      jsonrpc: '2.0',
      params: input,
    };
    return this.http.post<BaseResponse<BankDetails>>(
      this.baseurl + '/exposed/wallet/create_bank_information',
      body
    );
  }
  editBankInformation(
    input: BankDetails
  ): Observable<BaseResponse<BankDetails>> {
    let body = {
      jsonrpc: '2.0',
      params: input,
    };
    return this.http.post<BaseResponse<BankDetails>>(
      this.baseurl + '/exposed/wallet/edit_bank_information',
      body
    );
  }
  getBankList(): Observable<BaseResponse<BankDetails[]>> {
    let body = {
      jsonrpc: '2.0',
      params: {},
    };
    return this.http.post<BaseResponse<BankDetails[]>>(
      this.baseurl + '/exposed/wallet/get_banks_list',
      body
    );
  }
  getCompanyBankList(): Observable<BaseResponse<BankDetails[]>> {
    let body = {
      jsonrpc: '2.0',
      params: {},
    };
    return this.http.post<BaseResponse<BankDetails[]>>(
      this.baseurl + '/exposed/wallet/get_company_bank_list',
      body
    );
  }
  
  getServiceProviderBankList(): Observable<BaseResponse<BankDetails>> {
    let body = {
      params: {},
    };
    return this.http.post<BaseResponse<BankDetails>>(
      this.baseurl + '/exposed/wallet/get_service_provider_bank_list',
      body
    );
  }
  getMerchantBalance(): Observable<
    BaseResponse<{ balance: number; currency: string }>
  > {
    return this.http.post<BaseResponse<{ balance: number; currency: string }>>(
      this.baseurl + '/exposed/wallet/get_partner_balance',
      {}
    );
  }
  getUserBalance(): Observable<
    BaseResponse<{ balance: number; currency: string }>
  > {
    return this.http.post<BaseResponse<{ balance: number; currency: string }>>(
      `${environment.API_URL}/exposed/wallet/get_user_balance`,
      {}
    );
  }
  updateUserBalance(): void {
    this.getUserBalance().subscribe((res) => {
      if (res.ok) {
        const balance =
          res.result.balance +
          +(localStorage.getItem(environment.BALANCE_KEY) ?? 0);
        this.store.dispatch(
          setBalance({ balance, currency: res.result.currency })
        );
      }
    });
  }
  approveRejectBankRequest(
    id: number, state: string, note: string):
    Observable<BaseResponse<any>> {
    const body = {
      params: { id: id, state: state, note: note },
    };
    return this.http.post<BaseResponse<any>>(
      this.baseurl + '/exposed/wallet/approve_reject_bank_transfer_request',
      body
    );

  }

}
