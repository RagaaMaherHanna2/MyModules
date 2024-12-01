import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReportsRoutingModule } from './reports-routing.module';
import { CreateSalesReportComponent } from './create-sales-report/create-sales-report.component';
import { ListSalesReportsComponent } from './list-sales-report/list-sales-reports.component';
import { FormsModule } from '@angular/forms';
import { DropdownModule } from 'primeng/dropdown';
import { InputTextModule } from 'primeng/inputtext';
import { FileUploadModule } from 'primeng/fileupload';
import { MultiSelectModule } from 'primeng/multiselect';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { TableModule } from 'primeng/table';
import { BadgeModule } from 'primeng/badge';
import { CheckboxModule } from 'primeng/checkbox';
import { CardModule } from 'primeng/card';
import { DividerModule } from 'primeng/divider';
import { DialogModule } from 'primeng/dialog';
import { CalendarModule } from 'primeng/calendar';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { UploadSerialsDialogComponent } from 'src/app/shared/upload-serials-dialog/upload-serials-dialog.component';
import { SharedModule } from 'src/app/shared/shared.module';
import { ToggleButtonModule } from 'primeng/togglebutton';
import { CreateIncomeReportComponent } from './create-income-report/create-income-report.component';
import { IncomeReportsComponent } from './income-reports/income-reports.component';
import { FeesReportComponent } from './fees-report/fees-report.component';
import { CreateFeesReportComponent } from './create-fees-report/create-fees-report.component';
import { BatchesFinanceReportComponent } from './batches-SPfinance-report/batches-finance-report/batches-finance-report.component';
import { DetailsBatchesFinanceComponent } from './batches-SPfinance-report/details-batches-finance/details-batches-finance.component';
import { DailyFeesReportComponent } from './daily-fees-report/daily-fees-report.component';

@NgModule({
  declarations: [
    CreateSalesReportComponent,
    ListSalesReportsComponent,
    CreateIncomeReportComponent,
    IncomeReportsComponent,
    FeesReportComponent,
    CreateFeesReportComponent,
    BatchesFinanceReportComponent,
    DetailsBatchesFinanceComponent,
    DailyFeesReportComponent,
  ],
  imports: [
    BadgeModule,
    CalendarModule,
    CardModule,
    CheckboxModule,
    CommonModule,
    DialogModule,
    DividerModule,
    DropdownModule,
    FileUploadModule,
    FormsModule,
    HttpClientModule,
    InputTextModule,
    MultiSelectModule,
    ReportsRoutingModule,
    ReactiveFormsModule,
    ProgressSpinnerModule,
    SharedModule,
    TableModule,
    UploadSerialsDialogComponent,
    ToggleButtonModule,
  ],
})
export class ReportsModule {}
