import { MultiSelectModule } from 'primeng/multiselect';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { BalanceRoutingModule } from './balance-routing.module';
import { TransactionLogsComponent } from './transaction-logs/transaction-logs.component';
import { SalesReportComponent } from './sales-report/sales-report.component';
import { InputTextModule } from 'primeng/inputtext';

@NgModule({
  declarations: [TransactionLogsComponent, SalesReportComponent],
  imports: [
    CommonModule,
    BalanceRoutingModule,
    TableModule,
    CardModule,
    FormsModule,
    ReactiveFormsModule,
    MultiSelectModule,
    InputTextModule,
  ],
})
export class BalancModule {}
