import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SubMerchantRoutingModule } from './sub-merchants-routing.module';
import { SubMerchantsListComponent } from './sub-merchants-list/sub-merchants-list.component';
import { SubMerchantDetailsComponent } from './sub-merchant-details/sub-merchant-details.component';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { CheckboxModule } from 'primeng/checkbox';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { SharedModule } from 'src/app/shared/shared.module';
import { DialogModule } from 'primeng/dialog';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
@NgModule({
  declarations: [
    SubMerchantsListComponent,
    SubMerchantDetailsComponent,
  ],
  imports: [
    ButtonModule,
    CheckboxModule,
    CardModule,
    CommonModule,
    SubMerchantRoutingModule,
    ProgressSpinnerModule,
    SharedModule,
    TableModule,
    DialogModule,
    FormsModule,
    ReactiveFormsModule,
    InputTextModule,
    PasswordModule
  ],
})
export class SubMerchantsModule {}
