import { WalletService } from './../../../services/wallet/wallet.service';
import { environment } from './../../../../environments/environment';
import {
  BankTransferRequest,
  CREDIT_TYPE,
} from './../../../../models/wallet/models';
import {
  ConfirmationService,
  MessageService,
  LazyLoadEvent,
} from 'primeng/api';
import { Component } from '@angular/core';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { ExcelService } from 'src/app/services/excel.service';
import { Router } from '@angular/router';
import { Store, createSelector } from '@ngrx/store';
import { accessRightFeature } from 'src/store/accessRightSlice';

@Component({
  selector: 'app-credit-requests',
  templateUrl: './credit-requests.component.html',
  styleUrls: ['./credit-requests.component.scss'],
  providers: [MessageService, ConfirmationService],
})
export class CreditRequestsComponent {
  userCurrency: string = (localStorage.getItem(environment.CURRENCY_SYMBOL)|| 'null')
  items: GetListResponse<BankTransferRequest> = { data: [], totalCount: 0 };
  item: BankTransferRequest = {} as BankTransferRequest;
  submitted = false;
  pageSize: number = environment.PAGE_SIZE;
  dialog: boolean = false;
  lastFilter: LazyLoadEvent = { filter: {}, first: 0 } as LazyLoadEvent;
  filter: string = '';
  loading: boolean = false;
  role$ = this.store.select(
    createSelector(accessRightFeature, (state) => state.role)
  );
  isServiceProvider: boolean = false;

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
    private router: Router,
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
        this.isServiceProvider = true;
        this.service
          .getServiceProviderChargeRequests({
            limit: this.pageSize,
            offset: event.first as number,
            filter: this.filter,
            sorting: event.sortField,
            type: CREDIT_TYPE,
          })
          .subscribe((res) => {
            if (res.ok) {
              this.items.data = res.result.data;
              this.items.totalCount = res.result.totalCount;
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
            type: CREDIT_TYPE,
          })
          .subscribe((res) => {
            if (res.ok) {
              this.items.data = res.result.data;
              this.items.totalCount = res.result.totalCount;
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

  exportExcel() {
    this.role$.subscribe((roles) => {
      if (roles.includes('service_provider')) {
        this.service
          .getServiceProviderChargeRequests({
            offset: 0,
            limit: this.items.totalCount,
            filter: this.lastFilter.globalFilter,
            type: CREDIT_TYPE,
            sorting: '',
          })
          .subscribe((res: any) => {
            const data = res.result.data;
            data.map((r: BankTransferRequest) => {
              //delete r.bankTransferImage;
            });

            this.excelService.convertJSONtoExcel(
              data,
              [],
              $localize`Bank Transfer Requests`
            );
          });
      } else {
        this.service
          .getMerchantChargeRequests({
            offset: 0,
            limit: this.items.totalCount,
            filter: this.lastFilter.globalFilter,
            type: CREDIT_TYPE,
            sorting: '',
          })
          .subscribe((res: any) => {
            const data = res.result.data;
            data.map((r: BankTransferRequest) => {
              // delete r.bankTransferImage;
            });

            this.excelService.convertJSONtoExcel(
              data,
              [],
              $localize`Bank Transfer Requests`
            );
          });
      }
    });
  }
  download_attachment(elem: BankTransferRequest) {
   // window.open(elem.bankTransferImage, '_blank');
    
  }
  viewDetails(item: BankTransferRequest) {
    this.router.navigate(['dashboard/wallet/details', item.id]);
  }
}
