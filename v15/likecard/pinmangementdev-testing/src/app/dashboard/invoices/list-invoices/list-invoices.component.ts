import { Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { InvoicesService } from 'src/app/services/invoices/invoices.service';
import { ACTION_STATE } from 'src/app/shared/utils/constants';
import { environment } from 'src/environments/environment';
import { RequestInvoice } from 'src/models/invoices/invoices.model';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';
import { createSelector } from '@ngrx/store';
import { accessRightFeature } from 'src/store/accessRightSlice';

@Component({
  selector: 'app-list-invoices',
  templateUrl: './list-invoices.component.html',
  styleUrls: ['./list-invoices.component.scss'],
})
export class ListInvoicesComponent{
  invoices: GetListResponse<RequestInvoice> = { data: [], totalCount: 0 };
  pageSize = environment.PAGE_SIZE;
  loading: boolean = false;
  actionState = ACTION_STATE;
  locale = $localize.locale;
  page: number =0;
  theUserRole: string = '';
  invoiceType: string ='';
  accessRole$ = this.store.select(
    createSelector(accessRightFeature, (state) => state.role)
  );


  constructor(private invoicesService: InvoicesService, private store: Store) {}



  getInvoices(type: string): void {
    this.loading = true;
    this.invoicesService.listInvoices({offset: this.page * this.pageSize, limit: this.pageSize, type: type}).subscribe((res) => {
      this.invoices = res.result;
      this.loading = false;
    });
  }
  merchantListInvoices(type: string): void {
    this.loading = true;
    this.invoicesService.merchantListInvoices({offset: this.page * this.pageSize, limit: this.pageSize, type: type}).subscribe((res) => {
      this.invoices = res.result;
      this.loading = false;
    });
  }


  ngOnInit() {

    this.accessRole$.subscribe((roles) => {
      this.theUserRole = roles[0]
      if (this.theUserRole === 'service_provider') {
        this.getInvoices('')
      } else {
        this.merchantListInvoices('')
      }
    });
  }
  applyFilter(type: string){
    this.invoiceType = type;
    this.getInvoices(type)
  }




  toggleShowOnMerchantDashboard(Id: number): void {
    this.invoicesService.toggleShowOnMerchantDashboard(Id).subscribe((res) => {
      if (res.ok) {
        this.getInvoices(this.invoiceType)
      }
    });
  }
  changePage(event:{first:number, rows: number}) {
    this.page = event.first / this.pageSize ?? this.page;
    (this.theUserRole[0] === "")
    if (this.theUserRole === 'service_provider') {
      this.getInvoices(this.invoiceType)
    } else {
      this.merchantListInvoices(this.invoiceType)
    }
  }

  downloadAttachment(invoice: RequestInvoice): void {
    const link = document.createElement('a');
    link.href = `${environment.API_URL}${invoice.image}`;
    link.target= "_blank";
    link.download = `${invoice.merchant} (${invoice.from_date} - ${invoice.to_date}).pdf`;
    link.click();
    link.remove();
  }
}
