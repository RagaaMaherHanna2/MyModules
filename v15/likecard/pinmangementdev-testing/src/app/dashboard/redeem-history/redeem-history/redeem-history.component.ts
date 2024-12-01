import { Router } from '@angular/router';
import { environment } from '../../../../environments/environment.staging';
import { GetListResponse } from '../../../../models/responses/get-response.model';
import { RedeemOperation } from '../../../../models/Product/models';
import { Component } from '@angular/core';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { ExcelService } from 'src/app/services/excel.service';
import { Store } from '@ngrx/store';
import { RedeemService } from 'src/app/services/redeem/redeem.service';
@Component({
  selector: 'app-redeem-history',
  templateUrl: './redeem-history.component.html',
  styleUrls: ['./redeem-history.component.scss'],
  providers: [MessageService],
})
export class RedeemHistoryComponent {
  items: GetListResponse<RedeemOperation> = {
    data: [],
    totalCount: 0,
  };
  loading: boolean = false;
  pageSize: number = environment.PAGE_SIZE;
  lastFilter: LazyLoadEvent = { filter: {}, first: 0 } as LazyLoadEvent;
  filter: string = '';
  locale = $localize.locale;

  constructor(
    private service: RedeemService,
    private messageService: MessageService,
    private router: Router,
    private excelService: ExcelService
  ) {}

  loadList(event: LazyLoadEvent) {
    this.loading = true;
    this.lastFilter = event;
    this.service
      .getRedeemHistory({
        limit: this.pageSize,
        offset: event.first as number,
        serial: this.filter,
        id: 0,
      })
      .subscribe((res) => {
        if (res.ok) {
          this.items.data = res.result.data;
          this.items.totalCount = res.result.totalCount;
          this.loading = false;
        } else {
          this.messageService.add({
            severity: 'error',
            summary: $localize`Loading Redeem History Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
  }
  applyFilter(event: any) {
    this.filter = event.target.value;
    let ev: LazyLoadEvent = {};
    ev.first = 0;
    ev.sortField = '';
    this.loadList(ev);
  }

  exportExcel() {
    this.service
      .getRedeemHistory({
        offset: 0,
        limit: this.items.totalCount,
        serial: this.filter,
        id: 0,
      })
      .subscribe((res: any) => {
        const data = res.result.data;
        data.map((r: any) => {
          delete r.image;
        });
        this.excelService.convertJSONtoExcel(
          data,
          [
            $localize`ID`,
            $localize`Redemption Date`,
            $localize`Value`,
            $localize`User ID`,
            $localize`Transaction ID`,
          ],
          $localize`Redeem History`
        );
      });
  }

  goToDetails(redeemOperation: RedeemOperation): void {
    this.router.navigate([
      '/dashboard/redeem-history/details/',
      redeemOperation.id,
    ]);
  }
}
