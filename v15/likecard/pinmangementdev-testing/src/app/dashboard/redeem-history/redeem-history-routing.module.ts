import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { RedeemHistoryComponent } from './redeem-history/redeem-history.component';
import { RedeemHistoryDetailsComponent } from './redeem-history-details/redeem-history-details.component';

const routes: Routes = [
  {
    path: '',
    component: RedeemHistoryComponent,
  },
  {
    path: 'details/:id',
    component: RedeemHistoryDetailsComponent,
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class RedeemHistoryRoutingModule {}
