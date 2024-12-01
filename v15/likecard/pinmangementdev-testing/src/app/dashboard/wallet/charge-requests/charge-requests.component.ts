import { WalletService } from './../../../services/wallet/wallet.service';
import { environment } from './../../../../environments/environment';
import {
  BankTransferRequest,
  DEPOSIT_TYPE,
} from './../../../../models/wallet/models';
import { MessageService, LazyLoadEvent } from 'primeng/api';
import { Component, OnInit } from '@angular/core';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { ExcelService } from 'src/app/services/excel.service';
import { Store, createSelector } from '@ngrx/store';
import { accessRightFeature } from 'src/store/accessRightSlice';
@Component({
  selector: 'app-charge-requests',
  templateUrl: './charge-requests.component.html',
  styleUrls: ['./charge-requests.component.scss'],
})
export class ChargeRequestsComponent {
  items: GetListResponse<BankTransferRequest> = { data: [], totalCount: 0 };
  item: BankTransferRequest = {} as BankTransferRequest;
  submitted = false;
  pageSize: number = environment.PAGE_SIZE;
  // selectedItems: BankTransfer[] = [];
  dialog: boolean = false;
  lastFilter: LazyLoadEvent = { filter: {}, first: 0 } as LazyLoadEvent;
  filter: string = '';
  loading: boolean = false;
  role$ = this.store.select(
    createSelector(accessRightFeature, (state) => state.role)
  );
  userCurrency: string = (localStorage.getItem(environment.CURRENCY_SYMBOL)|| 'null')


  readonly orderStatus: {
    [key: string]: any;
  } = {
    approved: {
      label: $localize`Approved`,
      severity: 'success',
    },
    draft: {
      label: $localize`Pending`,
      severity: 'warning',
    },
    rejected: {
      label: $localize`Rejected`,
      severity: 'danger',
    },
  };
  constructor(
    private service: WalletService,
    private messageService: MessageService,
    private excelService: ExcelService,
    private store: Store
  ) {}

  setFilter(filter: string) {
    this.filter = filter;
    this.loadList(this.lastFilter);
  }
  openNew() {
    this.item = {} as BankTransferRequest;
    this.submitted = false;
    this.dialog = true;
  }
  hideDialog() {
    this.dialog = false;
    this.submitted = false;
  }

  loadList(event: LazyLoadEvent) {
    this.loading = true;
    this.lastFilter = event;
    this.role$.subscribe((roles) => {
      if (roles.includes('service_provider')) {
        this.service
          .getServiceProviderChargeRequests({
            limit: this.pageSize,
            offset: event.first as number,
            filter: this.filter,
            sorting: event.sortField,
            type: DEPOSIT_TYPE,
          })
          .subscribe((res) => {
            if (res.ok) {
              if (
                !res.result.data ||
                Object.keys(res.result.data).length === 0
              ) {
                this.items.data = [];
                this.items.totalCount = 0;
              } else {
                this.items.data = res.result.data;
                this.items.totalCount = res.result.totalCount;
              }
              this.loading = false;
            } else {
              this.messageService.add({
                severity: 'error',
                summary: 'Loading Request Failed',
                detail: res.message,
                life: 3000,
              });
            }
          });
      } else {
        this.service
          .getMerchantChargeRequests({
            limit: this.pageSize,
            offset: event.first as number,
            filter: this.filter,
            sorting: event.sortField,
            type: DEPOSIT_TYPE,
          })
          .subscribe((res) => {
            if (res.ok) {
              if (
                !res.result.data ||
                Object.keys(res.result.data).length === 0
              ) {
                this.items.data = [];
                this.items.totalCount = 0;
              } else {
                this.items.data = res.result.data;
                this.items.totalCount = res.result.totalCount;
              }
              this.loading = false;
            } else {
              this.messageService.add({
                severity: 'error',
                summary: 'Loading Request Failed',
                detail: res.message,
                life: 3000,
              });
            }
          });
      }
    });
  }

  downloadAttachment(item: BankTransferRequest): void {
    const link = document.createElement('a');
    link.href = `${environment.API_URL}${item.image}`;
    link.click();
    link.remove();
  }

  exportExcel() {
    this.role$.subscribe((roles) => {
      if (roles.includes('service_provider')) {
        this.service
          .getServiceProviderChargeRequests({
            offset: 0,
            limit: this.items.totalCount,
            filter: this.lastFilter.globalFilter,
            type: DEPOSIT_TYPE,
            sorting: '',
          })
          .subscribe((res) => {
            if (res.ok) {
              let data = res.result.data;
              if (!data || Object.keys(data).length === 0) {
                data = [];
              }
              this.excelService.convertJSONtoExcel(
                data,
                [],
                $localize`Bank Transfer Requests`
              );
            }
          });
      } else {
        this.service
          .getMerchantChargeRequests({
            offset: 0,
            limit: this.items.totalCount,
            filter: this.lastFilter.globalFilter,
            type: DEPOSIT_TYPE,
            sorting: '',
          })
          .subscribe((res) => {
            if (res.ok) {
              let data = res.result.data;
              if (!data || Object.keys(data).length === 0) {
                data = [];
              }
              this.excelService.convertJSONtoExcel(
                data,
                [],
                $localize`Bank Transfer Requests`
              );
            }
          });
      }
    });
  }
}
