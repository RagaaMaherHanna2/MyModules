import { Component, Inject, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { ReportsService } from '../../../services/reports/reports.service';
import { ACTION_STATE } from 'src/app/shared/utils/constants';
import { environment } from 'src/environments/environment';
import { RequestSaleReport } from '../../../../models/Reports/models';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { MerchantsService } from 'src/app/services/merchants/merchants.service';
import { MerchantsInviteList } from 'src/models/invites/invites.model';
import { createSelector } from '@ngrx/store';
import { accessRightFeature } from 'src/store/accessRightSlice';
import { LOCALE_ID } from '@angular/core';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-list-reports',
  templateUrl: './list-sales-reports.component.html',
  styleUrls: ['./list-sales-reports.component.scss'],
})
export class ListSalesReportsComponent {
  minDate: Date = new Date();
  maxDate: Date = new Date();

  reports: GetListResponse<RequestSaleReport> = { data: [], totalCount: 0 };
  pageSize = environment.PAGE_SIZE;
  loading: boolean = false;
  actionState = ACTION_STATE;
  locale = $localize.locale;
  page: number = 0;
  rangeDates: any;

  lastFilter: LazyLoadEvent = { filter: {}, first: 0 } as LazyLoadEvent;
  filter: string = '';
  product: string = '';
  selectedMerchant: any;
  merchants: GetListResponse<MerchantsInviteList>;
  options: { name: string; reference: string; id: any }[] = [
    { name: $localize`All`, reference: '', id: null },
  ];
  theUserRole: string = '';
  currentLanguage: String = this.localeId;

  accessRole$ = this.store.select(
    createSelector(accessRightFeature, (state) => state.role)
  );

  constructor(
    private reportsService: ReportsService,
    private store: Store,
    private messageService: MessageService,
    private merchantsService: MerchantsService,
    @Inject(LOCALE_ID) private localeId: string
  ) {}

  ngOnInit() {
    this.minDate.setMonth(this.minDate.getMonth() - 3);
    this.maxDate.setDate(this.maxDate.getDate());

    this.accessRole$.subscribe((roles) => {
      this.theUserRole = roles[0];
      if (this.theUserRole === 'service_provider') {
        this.merchantsService.getInvitesList().subscribe((res) => {
          if (res.ok) {
            this.merchants = res.result;
            this.merchants.data.forEach((merchant) => {
              this.options.push({
                name: merchant.name!,
                reference: merchant.reference!,
                id: merchant.id!,
              });
            });
          }
        });
      }
    });
  }

  loadList() {
    const datepipe: DatePipe = new DatePipe('en-US');
    this.loading = true;
    this.reportsService
      .listSalesReports({
        limit: this.pageSize,
        offset: this.page * this.pageSize,
        product: this.product ? this.product : undefined,
        merchant_filter: this.selectedMerchant
          ? this.selectedMerchant
          : undefined,
        from_date: this.rangeDates
          ? datepipe.transform(this.rangeDates[0], 'yyyy-MM-dd')
          : undefined,
        to_date: this.rangeDates
          ? datepipe.transform(this.rangeDates[1], 'yyyy-MM-dd')
          : undefined,
        // product_name: (this.selectedProduct!== undefined)? this.selectedProduct.product : '' ,
        // order_date:[].push(order)
      })
      .subscribe((res) => {
        if (res.ok) {
          this.reports = res.result;
          this.loading = false;
        } else {
          this.messageService.add({
            severity: 'error',
            summary: $localize`Loading Orders Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
  }

  clearRangeDates(): void {
    this.rangeDates = null;
  }

  getReports(): void {
    this.loading = true;
    this.reportsService
      .listSalesReports({
        offset: this.page * this.pageSize,
        limit: this.pageSize,
      })
      .subscribe((res) => {
        this.reports = res.result;
        this.loading = false;
      });
  }
  changePage(event: { first: number; rows: number }) {
    this.page = event.first / this.pageSize ?? this.page;
    this.getReports();
  }

  downloadAttachment(report: RequestSaleReport): void {
    const link = document.createElement('a');
    link.href = `${environment.API_URL}${report.file}`;
    link.target = '_blank';
    link.download = `Sales Report (${report.from_date} - ${report.to_date}).pdf`;
    link.click();
    link.remove();
  }
}
