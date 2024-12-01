import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { InvoicesRoutingModule } from './invoices-routing.module';
import { RequestInvoiceComponent } from './request-invoice/request-invoice.component';
import { ListInvoicesComponent } from './list-invoices/list-invoices.component';
import { CardModule } from 'primeng/card';
import { ReactiveFormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { DropdownModule } from 'primeng/dropdown';
import { CalendarModule } from 'primeng/calendar';
import { TableModule } from 'primeng/table';
import { SharedModule } from 'src/app/shared/shared.module';
import { ListBillsComponent } from './list-bills/list-bills.component';
import { SelectPaymentMethodComponent } from './select-payment-method/select-payment-method.component';
import { FormsModule } from '@angular/forms';
import { BankTransferPayComponent } from './bank-transfer-pay/bank-transfer-pay.component';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { FileUploadModule } from 'primeng/fileupload';
import { DividerModule } from 'primeng/divider';
import { BillPaymentDetailsComponent } from './bill-payment-details/bill-payment-details.component';
@NgModule({
  declarations: [
    RequestInvoiceComponent,
    ListInvoicesComponent,
    ListBillsComponent,
    SelectPaymentMethodComponent,
    BankTransferPayComponent,
    BillPaymentDetailsComponent, 
  ],
  imports: [
    ButtonModule,
    CalendarModule,
    CardModule,
    CommonModule,
    DropdownModule, 
    InvoicesRoutingModule,
    ReactiveFormsModule,
    SharedModule,
    TableModule,
    FormsModule, 
    FileUploadModule,
    DividerModule,
    ProgressSpinnerModule
  ]
})
export class InvoicesModule { }
