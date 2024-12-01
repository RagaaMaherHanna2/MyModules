import { DialogModule } from 'primeng/dialog';
import { ToolbarModule } from 'primeng/toolbar';
import { TableModule } from 'primeng/table';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { WalletRoutingModule } from './wallet-routing.module';
import { ChargeWalletComponent } from './charge-wallet/charge-wallet.component';
import { DropdownModule } from 'primeng/dropdown';
import { InputTextModule } from 'primeng/inputtext';
import { FileUploadModule } from 'primeng/fileupload';
import { DividerModule } from 'primeng/divider';
import { ChargeRequestsComponent } from './charge-requests/charge-requests.component';
import { BadgeModule } from 'primeng/badge';
import { CreditRequestsComponent } from './credit-requests/credit-requests.component';
import { CreditWalletComponent } from './credit-wallet/credit-wallet.component';
import { BankListComponent } from './bank-list/bank-list.component';
import { ChargeBalanceWithVoucherComponent } from './charge-balance-with-voucher/charge-balance-with-voucher.component';
import { CardModule } from 'primeng/card';
import { CreditRequestDetailsComponent } from './credit-request-details/credit-request-details.component';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { InputTextareaModule } from 'primeng/inputtextarea';

@NgModule({
  declarations: [
    ChargeWalletComponent,
    ChargeRequestsComponent,
    CreditRequestsComponent,
    CreditWalletComponent,
    BankListComponent,
    ChargeBalanceWithVoucherComponent,
    CreditRequestDetailsComponent,
  ],
  imports: [
    CardModule,
    CommonModule,
    DropdownModule,
    InputTextModule,
    FormsModule,
    FileUploadModule,
    TableModule,
    WalletRoutingModule,
    ToolbarModule,
    DividerModule,
    BadgeModule,
    ReactiveFormsModule,
    DialogModule,
    ProgressSpinnerModule,
    InputTextareaModule
  ],
})
export class WalletModule {}
