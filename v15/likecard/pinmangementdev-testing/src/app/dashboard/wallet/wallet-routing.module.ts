import { BankListComponent } from './bank-list/bank-list.component';
import { CreditWalletComponent } from './credit-wallet/credit-wallet.component';
import { CreditRequestsComponent } from './credit-requests/credit-requests.component';
import { ChargeRequestsComponent } from './charge-requests/charge-requests.component';
import { ChargeWalletComponent } from './charge-wallet/charge-wallet.component';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ChargeBalanceWithVoucherComponent } from './charge-balance-with-voucher/charge-balance-with-voucher.component';
import { CreditRequestDetailsComponent } from './credit-request-details/credit-request-details.component';

const routes: Routes = [
  { path: 'view-charge-request', component: ChargeRequestsComponent },
  { path: 'add-charge-request', component: ChargeWalletComponent },
  { path: 'view-credit-request', component: CreditRequestsComponent },
   { path: 'details/:id', component: CreditRequestDetailsComponent  },
  { path: 'add-credit-request', component: CreditWalletComponent },
  { path: 'bank-list', component: BankListComponent },
  {
    path: 'redeem-balance-voucher',
    component: ChargeBalanceWithVoucherComponent,
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class WalletRoutingModule {}
