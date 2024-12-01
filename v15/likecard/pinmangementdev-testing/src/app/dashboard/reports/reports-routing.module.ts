import { BatchesFinanceReportComponent } from './batches-SPfinance-report/batches-finance-report/batches-finance-report.component';
import { DetailsBatchesFinanceComponent } from './batches-SPfinance-report/details-batches-finance/details-batches-finance.component';
import { CreateFeesReportComponent } from './create-fees-report/create-fees-report.component';
import { CreateIncomeReportComponent } from './create-income-report/create-income-report.component';
import { CreateSalesReportComponent } from './create-sales-report/create-sales-report.component';
import { DailyFeesReportComponent } from './daily-fees-report/daily-fees-report.component';
import { FeesReportComponent } from './fees-report/fees-report.component';
import { IncomeReportsComponent } from './income-reports/income-reports.component';
import { ListSalesReportsComponent } from './list-sales-report/list-sales-reports.component';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: 'create-sale-report', component: CreateSalesReportComponent },
  { path: 'list-sales-reports', component: ListSalesReportsComponent },
  { path: 'create-income-report', component: CreateIncomeReportComponent },
  { path: 'income-reports', component: IncomeReportsComponent },
  { path: 'create-fees-report', component: CreateFeesReportComponent },
  { path: 'fees-reports', component: FeesReportComponent },
  { path: 'daily-fees-reports', component: DailyFeesReportComponent },
  { path: 'batches-report', component: BatchesFinanceReportComponent },
  {
    path: 'batches-report/details/:id',
    component: DetailsBatchesFinanceComponent,
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class ReportsRoutingModule {}
