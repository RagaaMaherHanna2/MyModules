import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CheckBalanceComponent } from './check-balance/check-balance.component';
import { OperationsHistoryComponent } from './operations-history/operations-history.component';

const routes: Routes = [
  {
    path: 'check-balance',
    component: CheckBalanceComponent,
  },
  {
    path: 'history/:code',
    component: OperationsHistoryComponent,
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class PrepaidRoutingModule { }
