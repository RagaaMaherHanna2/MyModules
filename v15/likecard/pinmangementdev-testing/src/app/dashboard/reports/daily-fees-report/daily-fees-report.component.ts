import { Component } from '@angular/core';
import { FormBuilder, FormControl, Validators } from '@angular/forms';
import { Store } from '@ngrx/store';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { BehaviorSubject } from 'rxjs';
import { ExcelService } from 'src/app/services/excel.service';
import { MerchantsService } from 'src/app/services/merchants/merchants.service';
import { ReportsService } from 'src/app/services/reports';
import { environment } from 'src/environments/environment';
import {
  DailyFees,
  DailyFeesReportbody,
  DailyFeesRequestFormType,
} from 'src/models/Reports/models';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { closeLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-daily-fees-report',
  templateUrl: './daily-fees-report.component.html',
  styleUrls: ['./daily-fees-report.component.scss'],
})
export class DailyFeesReportComponent {
  constructor(
    private formBuilder: FormBuilder,
    private store: Store,
    private reportsService: ReportsService,
    private merchantsService: MerchantsService,
    private messageService: MessageService,
    private excelService: ExcelService
  ) {}
  merchants: { name: string; id: number }[] = [];
  SPs: { name: string; id: number }[] = [];
  offset: number = 0;
  loadingMerchants = new BehaviorSubject(false);
  feesReportForm = this.formBuilder.group<DailyFeesRequestFormType>({
    sp: new FormControl<number | null>(null, [Validators.required]),
    merchant: new FormControl<number | null>(null, [Validators.required]),
  });
  dailyFeesReportBody: DailyFeesReportbody;
  first: LazyLoadEvent = { first: 0 } as LazyLoadEvent;
  loading: boolean = false;
  pageSize: number = environment.PAGE_SIZE;
  items: GetListResponse<DailyFees> = {
    data: [],
    totalCount: 0,
  };
  userCurrency: string =
    localStorage.getItem(environment.CURRENCY_SYMBOL) || 'null';
  showResult: boolean;
  ngOnInit() {
    this.merchantsService.getAccountantManagerSPs().subscribe((res) => {
      this.store.dispatch(closeLoadingDialog());
      if (res.ok) {
        let serviceProviders = res.result.data;
        serviceProviders.forEach((sp) => {
          this.SPs.push(sp);
        });
      }
    });
  }
  getMerchants(sp: number) {
    this.merchants = [];
    this.loadingMerchants.next(true);
    this.merchantsService
      .getInvitesList(this.offset, 1000, sp)
      .subscribe((res) => {
        if (res.ok) {
          this.loadingMerchants.next(false);
          res.result.data.forEach((merchant) => {
            this.merchants.push({
              name: merchant.name!,
              id: merchant.id!,
            });
          });
        }
      });
  }
  submit() {
    let ev: LazyLoadEvent = {};
    ev.first = 0;
    this.loadList(ev);
  }

  loadList(event: LazyLoadEvent) {
    (this.dailyFeesReportBody = {
      service_provider_id: this.feesReportForm.value.sp!,
      merchant_id: this.feesReportForm.value.merchant!,
      limit: 10,
      offset: event.first as number,
    }),
      (this.loading = true);
    this.reportsService
      .listDailyFeesReports(this.dailyFeesReportBody)
      .subscribe((res) => {
        if (res.ok) {
          this.showResult = true;
          this.items.data = res.result.data;
          this.items.totalCount = res.result.totalCount;
          this.loading = false;
        } else {
          this.messageService.add({
            severity: 'error',
            summary: $localize`Loading Daily Fees Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
  }
  exportExcel() {
    this.reportsService
      .listDailyFeesReports({
        offset: 0,
        limit: this.items.totalCount,
        service_provider_id: this.feesReportForm.value.sp!,
        merchant_id: this.feesReportForm.value.merchant!,
      })
      .subscribe((res: any) => {
        const data = res.result.data;

        this.excelService.convertJSONtoExcel(
          data,
          [
            $localize`Report Date`,
            $localize`Service Provider ID`,
            $localize`Service Provider Name`,
            $localize`Merchant ID`,
            $localize`Merchant Name`,
            $localize`Pull Quantity`,
            $localize`Pull Fees Total`,
            $localize`Redeem Quantity`,
            $localize`Redeem Fees Total`,
          ],
          $localize`Daily Fees Report ${data[0]['service_provider_name']}- ${data[0]['merchant_name']}`
        );
      });
  }

  onPageChange(event: LazyLoadEvent) {
    this.loadList(event); // Reload data when page changes
  }
}
