import { SalesReportComponent } from './sales-report/sales-report.component';
import { TransactionLogsComponent } from './transaction-logs/transaction-logs.component';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: 'list', component: TransactionLogsComponent },
  { path: 'report', component: SalesReportComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class BalanceRoutingModule {}
