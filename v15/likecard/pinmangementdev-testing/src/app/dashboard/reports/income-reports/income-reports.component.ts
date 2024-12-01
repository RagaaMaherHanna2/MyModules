import { DatePipe } from '@angular/common';
import { Component, Inject, LOCALE_ID } from '@angular/core';
import { createSelector, Store } from '@ngrx/store';
import { MessageService } from 'primeng/api';
import { ReportsService } from 'src/app/services/reports';
import { environment } from 'src/environments/environment';
import { IncomeReport } from 'src/models/Reports/models';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { accessRightFeature } from 'src/store/accessRightSlice';

@Component({
  selector: 'app-income-reports',
  templateUrl: './income-reports.component.html',
  styleUrls: ['./income-reports.component.scss'],
})
export class IncomeReportsComponent {
  constructor(
    private reportsService: ReportsService,
    private messageService: MessageService,
    private store: Store,
    @Inject(LOCALE_ID) private localeId: string
  ) {}

  minDate: Date = new Date();
  maxDate: Date = new Date();

  reports: GetListResponse<IncomeReport> = { data: [], totalCount: 0 };
  pageSize = environment.PAGE_SIZE;
  loading: boolean = false;
  locale = $localize.locale;
  page: number = 0;
  rangeDates: any;
  currentLanguage: String = this.localeId;
  fromDate: Date;

  ngOnInit() {
    this.minDate.setMonth(this.minDate.getMonth() - 3);
    this.maxDate.setDate(this.maxDate.getDate());
  }

  loadList(fromDate: string = '') {
    console.log(fromDate);
    const datepipe: DatePipe = new DatePipe('en-US');
    this.loading = true;
    this.reportsService
      .listIncomeReports({
        limit: this.pageSize,
        offset: this.page * this.pageSize,
        from_date: fromDate,
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
      .listIncomeReports({
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

  downloadAttachment(report: IncomeReport): void {
    const link = document.createElement('a');
    link.href = `${environment.API_URL}${report.report_url}`;
    link.target = '_blank';
    link.download = `Income Report (${report.from_date} - ${report.to_date}).pdf`;
    link.click();
    link.remove();
  }

  applyFilter() {
    let fromDate = this.fromDate;
    const datepipe: DatePipe = new DatePipe('en-US');
    let from_date = datepipe.transform(fromDate, 'yyyy-MM-dd');
    this.loadList(from_date || '');
  }
}
