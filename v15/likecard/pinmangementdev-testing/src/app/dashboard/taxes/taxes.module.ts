import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TaxesRoutingModule } from './taxes-routing.module';
import { CreateTaxComponent } from './create-tax/create-tax.component';
import { ListTaxesComponent } from './list-taxes/list-taxes.component';
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

@NgModule({
  declarations: [
    CreateTaxComponent,
    ListTaxesComponent,
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
    TaxesRoutingModule,
    ReactiveFormsModule,
    ProgressSpinnerModule,
    SharedModule,
    TableModule,
    UploadSerialsDialogComponent,
    ToggleButtonModule
  ],
})
export class TaxesModule {}
