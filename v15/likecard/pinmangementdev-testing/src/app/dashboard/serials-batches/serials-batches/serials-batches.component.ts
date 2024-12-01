import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { SerialsBatchesService } from 'src/app/services/serials-batches/serials-batches.service';
import { environment } from 'src/environments/environment';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { SerialsBatch } from 'src/models/serial/model';
import { openLoadingDialog, closeLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-serials-batches',
  templateUrl: './serials-batches.component.html',
  styleUrls: ['./serials-batches.component.scss'],
})
export class SerialsBatchesComponent {
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
  constructor(
    private service: SerialsBatchesService,
    private router: Router,
    private messageService: MessageService,
    private store: Store
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

  sendViaEmail(serialsBatch: SerialsBatch): void {
    this.store.dispatch(openLoadingDialog());
    this.service.sendBatchSerialViaEmail(serialsBatch.id).subscribe((res) => {
      if (res.ok) {
        this.messageService.add({
          severity: 'success',
          summary: $localize`Email Sent Successfully`,
          detail: res.message,
          life: 3000,
        });
        this.store.dispatch(closeLoadingDialog());
      } else {
        this.store.dispatch(closeLoadingDialog());
        this.messageService.add({
          severity: 'error',
          summary: $localize`Sending Email Failed`,
          detail: res.message,
          life: 3000,
        });
      }
    });
  }

  navigateToProductDetails(serialsBatch: SerialsBatch): void {
    this.router.navigate([
      'dashboard/product/details/',
      serialsBatch.product_id,
    ]);
  }
  setStateFilter(stateId: string) {
    this.state_filter = stateId;
    this.applyFilter();
  }
}
