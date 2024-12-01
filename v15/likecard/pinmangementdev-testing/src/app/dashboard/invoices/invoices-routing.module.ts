import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { RequestInvoiceComponent } from './request-invoice/request-invoice.component';
import { ListInvoicesComponent } from './list-invoices/list-invoices.component';
import { ListBillsComponent } from './list-bills/list-bills.component';
import { SelectPaymentMethodComponent } from './select-payment-method/select-payment-method.component';
import { BankTransferPayComponent } from './bank-transfer-pay/bank-transfer-pay.component';
import { BillPaymentDetailsComponent } from './bill-payment-details/bill-payment-details.component';

const routes: Routes = [
  {
    path: "create",
    component: RequestInvoiceComponent,
  },
  {
    path: "list",
    component: ListInvoicesComponent,
  },
  {
    path: "bills",
    component: ListBillsComponent,
  },
  {
    path: "bills/:id",
    component: BillPaymentDetailsComponent,
  },
  {
    path: "bills/pay/:id",
    component: SelectPaymentMethodComponent,
  },
  {
    path: "bills/pay/:id/invoice_payment",
    component: BankTransferPayComponent,
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class InvoicesRoutingModule { }
