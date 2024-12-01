import { ToolbarModule } from 'primeng/toolbar';
import { SplitButtonModule } from 'primeng/splitbutton';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CalendarModule } from 'primeng/calendar';
import { PackageRoutingModule } from './package-routing.module';
import { CreatePackageComponent } from './create-package/create-package.component';
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
import { EditPackageComponent } from './edit-package/edit-package.component';
import { ListPackageComponent } from './list-package/list-package.component';
import { PackageDetailsComponent } from './package-details/package-details.component';
import { DividerModule } from 'primeng/divider';
import { CardModule } from 'primeng/card';
import { PackageReportComponent } from './package-report/package-report.component';
import { PackageMerchantsComponent } from './package-merchants/package-merchants.component';
import { EditMerchantComponent } from './edit-merchant/edit-merchant.component';
import { InviteMerchantComponent } from './invite-merchant/invite-merchant.component';
import { PickListModule } from 'primeng/picklist';
import { AddVouchersComponent } from './add-vouchers/add-vouchers.component';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { RadioButtonModule } from 'primeng/radiobutton';

@NgModule({
  declarations: [
    CreatePackageComponent,
    EditPackageComponent,
    ListPackageComponent,
    PackageDetailsComponent,
    PackageReportComponent,
    PackageMerchantsComponent,
    EditMerchantComponent,
    InviteMerchantComponent,
    AddVouchersComponent,
  ],
  imports: [
    BadgeModule,
    CalendarModule,
    CardModule,
    CheckboxModule,
    CommonModule,
    DividerModule,
    DropdownModule,
    FileUploadModule,
    FormsModule,
    HttpClientModule,
    InputTextModule,
    MultiSelectModule,
    PackageRoutingModule,
    PickListModule,
    ProgressSpinnerModule,
    RadioButtonModule,
    ReactiveFormsModule,
    SplitButtonModule,
    TableModule,
    ToolbarModule,
  ],
})
export class PackageModule {}
