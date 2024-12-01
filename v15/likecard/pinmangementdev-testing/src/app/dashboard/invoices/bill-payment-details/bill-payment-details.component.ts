import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { InvoicesService } from 'src/app/services/invoices/invoices.service';
import { environment } from 'src/environments/environment';
import { Bill } from 'src/models/invoices/invoices.model';
import { BankTransferRequest } from 'src/models/wallet/models';

@Component({
  selector: 'app-bill-payment-details',
  templateUrl: './bill-payment-details.component.html',
  styleUrls: ['./bill-payment-details.component.scss']
})

export class BillPaymentDetailsComponent {
  bill: Bill;
  constructor(
    private activatedRoute: ActivatedRoute,
    private invoicesService: InvoicesService,
    private store: Store,
    private router: Router
  ) { }

  bankTransferRequest: BankTransferRequest;
  userCurrency: string = (localStorage.getItem(environment.CURRENCY_SYMBOL)|| 'null')
  note: string = '';
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
  ngOnInit(): void {




    this.activatedRoute.params.subscribe((params) => {
      this.invoicesService.getBills(0, 0, Number(params['id'])).subscribe((res) => {
        if (res.ok) {
          this.bill = res.result.data[0];
        }
      });
      
      this.invoicesService
        .getBillPaymentDetails(+params['id'])
        .subscribe((res) => {
          if (res.ok) {
            this.bankTransferRequest = res.result.data[0];
          }
        });
    });
  }
  downloadAttachment(item: BankTransferRequest): void {
    const link = document.createElement('a');
    link.href = `${environment.API_URL}${item.image}`;
    link.click();
    link.remove();
  }

}