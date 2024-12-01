import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { SerialsBatchesService } from 'src/app/services/serials-batches/serials-batches.service';
import { environment } from 'src/environments/environment';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { SerialsBatch } from 'src/models/serial/model';
import { SelectItem } from 'primeng/api';

@Component({
  selector: 'app-batches-finance-report',
  templateUrl: './batches-finance-report.component.html',
  styleUrls: ['./batches-finance-report.component.scss'],
})
export class BatchesFinanceReportComponent {
  items: GetListResponse<SerialsBatch> = {
    data: [],
    totalCount: 0,
  };
  loading: boolean = false;
  pageSize: number = environment.PAGE_SIZE;
  batch_Sequence_filter: string = '';
  product_name_filter: string = '';
  upload_date_filter: string = '';
  vendor_name_filter: string = '';
  invoice_ref_filter: string = '';
  category_name_filter: string = '';
  state_filter: string = '';
  matchModeOptions: SelectItem[];
  constructor(
    private service: SerialsBatchesService,
    private router: Router,
    private messageService: MessageService
  ) {}
  loadList(event: LazyLoadEvent) {
    this.loading = true;
    this.service
      .getBatchesList({
        limit: this.pageSize,
        offset: event.first as number,
        id: 0,
        sorting: event.sortField
          ? `${event.sortField} ${event.sortOrder === 1 ? 'asc' : 'desc'}`
          : '',
        batch_sequence: this.batch_Sequence_filter,
        create_date: this.upload_date_filter,
        product_name: this.product_name_filter,
        vendor_name: this.vendor_name_filter,
        invoice_ref: this.invoice_ref_filter,
        category_name: this.category_name_filter,
        state: this.state_filter,
      })
      .subscribe((res) => {
        if (res.ok) {
          this.items.data = res.result.data;
          this.items.totalCount = res.result.totalCount;
          this.loading = false;
        } else {
          this.messageService.add({
            severity: 'error',
            summary: $localize`Loading Product Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
  }

  applyFilter() {
    let ev: LazyLoadEvent = {};
    ev.first = 0;
    ev.sortField = '';
    this.loadList(ev);
  }

  navigateToBatchDetails(serialsBatch: SerialsBatch): void {
    this.router.navigate([
      `dashboard/reports/batches-report/details/${serialsBatch.id}`,
    ]);
  }
  setStateFilter(stateId: string) {
    this.state_filter = stateId;
    this.applyFilter();
  }
}
