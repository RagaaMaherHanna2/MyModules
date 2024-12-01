import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { InvoicesService } from 'src/app/services/invoices/invoices.service';
import { environment } from 'src/environments/environment';
import { Bill } from 'src/models/invoices/invoices.model';
import { GetListResponse } from 'src/models/responses/get-response.model';

@Component({
  selector: 'app-list-bills',
  templateUrl: './list-bills.component.html',
  styleUrls: ['./list-bills.component.scss'],
})
export class ListBillsComponent {
  items: GetListResponse<Bill> = {
    totalCount: 0,
    data: [],
  };
  limit = environment.PAGE_SIZE;
  offset: number = 0;
  loading: boolean = true;
  userCurrency: string = (localStorage.getItem(environment.CURRENCY_SYMBOL)|| 'null')

  constructor(private invoicesService: InvoicesService,
    private router: Router) { }

  loadList(): void {
    this.loading = true;
    this.invoicesService.getBills(this.offset,this.limit, 0)
      .subscribe((res) => {
        if (res.ok) {
          this.items = res.result;
        }
        this.loading = false;
      });
  }

  changePage({ first, rows }: { first: number; rows: number }): void {
    this.offset = first;
    this.limit = rows;
    this.loadList();
  }
  pay(bill: Bill) {
    this.router.navigate([`/dashboard/invoices/bills/pay/${bill.id}`]);
  }
  getPaymentDetails(bill: Bill) {
    this.router.navigate([`/dashboard/invoices/bills/${bill.id}`]);
  }
}
